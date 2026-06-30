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

LOGIN_URL = "https://vms.laboredge.com/signin"
DATA_URL = "https://vms.laboredge.com/supplier/jobs/view/alljobs"

USERNAME = "pooja.raut@patternshiring.com"
PASSWORD = "Patterns@123"
ORG_CODE = "NS"

edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 35)

try:
    # 1. DATABASE INITIALIZATION
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS laboredge_jobs (
                job_id VARCHAR(50) PRIMARY KEY,
                status TEXT,
                facility TEXT,
                state TEXT,
                job_type TEXT,
                profession TEXT,
                specialty TEXT,
                shift TEXT,
                start_date TEXT,
                posted_on TEXT,
                city TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

    # 2. LOGIN PROCESS
    print("Navigating to LaborEdge Login...")
    driver.get(LOGIN_URL)
    
    # Wait for fields and enter data
    email_field = wait.until(EC.element_to_be_clickable((By.ID, "email")))
    email_field.send_keys(USERNAME)
    
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    
    org_field = driver.find_element(By.ID, "organizationCode")
    org_field.send_keys(ORG_CODE)
    
    time.sleep(1) # Wait for Angular validation to enable the button

    print("Submitting Login...")
    login_btn = driver.find_element(By.XPATH, "//span[text()='LOGIN']/ancestor::button")
    
    # Use JS click because PrimeNG buttons are often 'disabled' in DOM but clickable via JS
    driver.execute_script("arguments[0].click();", login_btn)

    # 3. NAVIGATION TO JOBS
    print("Waiting for redirection...")
    time.sleep(10)
    driver.get(DATA_URL)
    
    # Wait for the PrimeNG table to render
    print("Waiting for data table...")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-datatable-tbody")))
    time.sleep(5) 

    scraped_data = []
    current_page = 1

    # 4. SCRAPING LOOP
    while True:
        print(f"Scraping Page {current_page}...")
        
        # In LaborEdge/PrimeNG, data rows usually have the class 'p-selectable-row'
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.p-datatable-selectable-row")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 10: continue
            
            # Helper to clean up the span/title structure found in LaborEdge
            def get_text(cell):
                try:
                    # LaborEdge uses <span title="..."> for their ellipsis cells
                    span = cell.find_element(By.TAG_NAME, "span")
                    return span.get_attribute("title").strip() if span.get_attribute("title") else span.text.strip()
                except:
                    return cell.text.strip()

            scraped_data.append({
                "job_id": get_text(cells[0]),
                "status": get_text(cells[2]),
                "facility": get_text(cells[3]),
                "state": get_text(cells[4]),
                "job_type": get_text(cells[5]),
                "profession": get_text(cells[6]),
                "specialty": get_text(cells[7]),
                "shift": get_text(cells[8]),
                "start_date": get_text(cells[9]),
                "posted_on": get_text(cells[10]),
                "city": get_text(cells[15]) if len(cells) > 15 else "N/A"
            })

        print(f"Captured {len(rows)} rows.")

        # PAGINATION (LaborEdge specific)
        try:
            # Look for the 'pi-angle-right' icon inside the paginator
            next_btn_icon = driver.find_element(By.CLASS_NAME, "pi-angle-right")
            next_btn = next_btn_icon.find_element(By.XPATH, "./ancestor::button")
            
            if next_btn.is_enabled() and "disabled" not in next_btn.get_attribute("class"):
                driver.execute_script("arguments[0].click();", next_btn)
                current_page += 1
                time.sleep(6) # Wait for Angular to refresh table
            else:
                print("No more pages.")
                break
        except Exception:
            break

    # 5. POSTGRES SYNC
    if scraped_data:
        print(f"Syncing {len(scraped_data)} records...")
        df = pd.DataFrame(scraped_data).drop_duplicates(subset=['job_id'])
        df.to_sql('laboredge_staging', engine, if_exists='replace', index=False)

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO laboredge_jobs (job_id, status, facility, state, job_type, profession, specialty, shift, start_date, posted_on, city)
                SELECT job_id, status, facility, state, job_type, profession, specialty, shift, start_date, posted_on, city FROM laboredge_staging
                ON CONFLICT (job_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    facility = EXCLUDED.facility,
                    state = EXCLUDED.state,
                    job_type = EXCLUDED.job_type,
                    profession = EXCLUDED.profession,
                    specialty = EXCLUDED.specialty,
                    shift = EXCLUDED.shift,
                    start_date = EXCLUDED.start_date,
                    posted_on = EXCLUDED.posted_on,
                    city = EXCLUDED.city,
                    last_seen = CURRENT_TIMESTAMP;
                
                DELETE FROM laboredge_jobs WHERE job_id NOT IN (SELECT job_id FROM laboredge_staging);
                DROP TABLE laboredge_staging;
            """))
        print("Success: LaborEdge data synchronized.")
    else:
        print("No data captured. Verify the table cell indices.")

except Exception as e:
    print(f"Fatal Error: {e}")
finally:
    driver.quit()
