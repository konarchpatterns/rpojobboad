import time
import pandas as pd
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
db_user = "development"
db_pass = quote_plus("PATTERNS@123") 
db_host = "localhost"
db_port = "5432"
db_name = "jobboard"
DB_URL = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

LOGIN_URL = "https://shccares.blueskymss.com/Login.html"
DATA_URL = "https://shccares.blueskymss.com/CrossSite/objextpage.aspx?l=SubcontractorNeedsModuleURI&nm=1&t=2"

USERNAME = "dhruvil.jaiswal"
PASSWORD = "Patterns@2026"

edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 45) # Increased timeout further

try:
    # 1. DATABASE INITIALIZATION
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bluesky_jobs (
                job_id VARCHAR(50) PRIMARY KEY,
                facility TEXT,
                unit TEXT,
                start_date TEXT,
                end_date TEXT,
                duration TEXT,
                shift TEXT,
                profession TEXT,
                city TEXT,
                state TEXT,
                pay_rate TEXT,
                description TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

    # 2. LOGIN PROCESS
    print("Navigating to BlueSky Login...")
    driver.get(LOGIN_URL)
    time.sleep(5)

    # Handle Login Iframe
    if len(driver.find_elements(By.TAG_NAME, "iframe")) > 0:
        driver.switch_to.frame(0)

    print("Entering credentials...")
    wait.until(EC.visibility_of_element_located((By.ID, "txtLogin"))).send_keys(USERNAME)
    driver.find_element(By.ID, "txtPassword").send_keys(PASSWORD)
    
    login_btn = driver.find_element(By.ID, "btnLogin")
    driver.execute_script("arguments[0].click();", login_btn)

    # 3. NAVIGATION TO JOBS
    driver.switch_to.default_content()
    print("Waiting for redirection...")
    time.sleep(10)
    
    print("Navigating to Jobs module URL...")
    driver.get(DATA_URL)
    time.sleep(8) # Allow time for the module wrapper to load

    # CHECK FOR IFRAME ON THE JOBS PAGE
    print("Checking if jobs table is inside an iframe...")
    job_iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if job_iframes:
        print(f"Found {len(job_iframes)} iframe(s) on jobs page. Switching...")
        driver.switch_to.frame(0)

    print("Waiting for data table to render...")
    try:
        # Wait for the tbody specifically
        wait.until(EC.presence_of_element_located((By.ID, "tbl_0_0_body_")))
    except:
        print("Table ID not found, attempting to find any table row...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.active, tr.preactive")))

    # 4. SCRAPING
    print("Parsing rows...")
    scraped_data = []
    # Target all rows starting with tr_0_0_ but ignore the header suffix _h_
    rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'tr_0_0_') and not(contains(@id, '_h_'))]")
    
    for row in rows:
        def get_val(prefix):
            try:
                # Search for element with ID starting with prefix inside THIS row
                return row.find_element(By.CSS_SELECTOR, f"[id*='{prefix}']").text.strip()
            except:
                return "N/A"

        job_info = {
            "job_id": get_val("IdCell"),
            "facility": get_val("FacilityNameCell"),
            "unit": get_val("UnitNameCell"),
            "start_date": get_val("StartDateCell"),
            "end_date": get_val("EndDateCell"),
            "duration": get_val("DurationCell"),
            "shift": get_val("DesiredShiftCell"),
            "profession": get_val("DegreeNameCell"),
            "city": get_val("CityCell"),
            "state": get_val("StateIDNameCell"),
            "pay_rate": get_val("PlPayRateCell"),
            "description": get_val("UnitDescriptionCell")
        }
        
        if job_info["job_id"] != "N/A":
            scraped_data.append(job_info)

    print(f"Scraped {len(scraped_data)} jobs.")

    # 5. POSTGRES SYNC
    if scraped_data:
        df = pd.DataFrame(scraped_data).drop_duplicates(subset=['job_id'])
        df.to_sql('bluesky_staging', engine, if_exists='replace', index=False)
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO bluesky_jobs (job_id, facility, unit, start_date, end_date, duration, shift, profession, city, state, pay_rate, description)
                SELECT job_id, facility, unit, start_date, end_date, duration, shift, profession, city, state, pay_rate, description FROM bluesky_staging
                ON CONFLICT (job_id) DO UPDATE SET
                    facility = EXCLUDED.facility, unit = EXCLUDED.unit, start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date, duration = EXCLUDED.duration, shift = EXCLUDED.shift,
                    profession = EXCLUDED.profession, city = EXCLUDED.city, state = EXCLUDED.state,
                    pay_rate = EXCLUDED.pay_rate, description = EXCLUDED.description, last_seen = CURRENT_TIMESTAMP;
                DELETE FROM bluesky_jobs WHERE job_id NOT IN (SELECT job_id FROM bluesky_staging);
                DROP TABLE bluesky_staging;
            """))
        print("Database sync complete.")
    else:
        print("No data found to sync.")

except Exception as e:
    print(f"Fatal Error: {e}")
finally:
    driver.quit()
