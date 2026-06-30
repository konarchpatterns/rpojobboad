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
LOGIN_URL = "https://vms.hwlmsp.com/shiftrock/user/login"
DATA_URL = "https://vms.hwlmsp.com/shiftrock/requisitionLocum/agencyLocumRequisition"
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Windows#1"

edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 30) # Increased to 30s

def scrape_modal_details():
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content")))
        time.sleep(2.5) 
        def find_val(label_text):
            try:
                path = f"//span[contains(normalize-space(), '{label_text}')]/following-sibling::div"
                return driver.find_element(By.XPATH, path).text.strip()
            except: return "N/A"

        data = {
            "address": find_val("Facility Address"),
            "guaranteed_hours": find_val("Guaranteed Hours"),
            "weeks": find_val("Weeks"),
            "full_dates": find_val("Requisition Start & End Date")
        }
        close_btn = driver.find_element(By.CSS_SELECTOR, "button.close")
        driver.execute_script("arguments[0].click();", close_btn)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-backdrop")))
        return data
    except:
        return {"address": "N/A", "guaranteed_hours": "N/A", "weeks": "N/A", "full_dates": "N/A"}

try:
    # 1. DB INIT
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hwl (
                job_id VARCHAR(50) PRIMARY KEY,
                facility TEXT,
                job_title TEXT,
                specialty TEXT,
                address TEXT,
                guaranteed_hours TEXT,
                weeks TEXT,
                full_dates TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

    # 2. LOGIN (Enhanced)
    print("Navigating to Login...")
    driver.get(LOGIN_URL)
    time.sleep(5) # Hard wait for initial redirects

    print("Checking for iframes...")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print(f"Found {len(iframes)} iframe(s). Switching to the first one...")
        driver.switch_to.frame(0)

    print("Locating login fields...")
    # Try multiple common selectors for the username field
    u_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username'], input[type='text'], #username")))
    u_field.clear()
    u_field.send_keys(USERNAME)
    
    p_field = driver.find_element(By.CSS_SELECTOR, "input[name='password'], input[type='password'], #password")
    p_field.clear()
    p_field.send_keys(PASSWORD)
    
    login_btn = driver.find_element(By.XPATH, "//button[contains(., 'Login')] | //input[@type='submit'] | //button[@type='submit']")
    login_btn.click()
    
    # Switch back to main content if we were in an iframe
    driver.switch_to.default_content()

    # 3. SCRAPE
    print("Waiting for page load...")
    time.sleep(10)
    driver.get(DATA_URL)
    
    scraped_data = []
    current_page = 1

    while True:
        print(f"Scraping Page {current_page}...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        time.sleep(5)
        
        req_links = driver.find_elements(By.CSS_SELECTOR, "#requisitionContainer ul li a")
        if not req_links: break

        for i in range(len(req_links)):
            current_links = driver.find_elements(By.CSS_SELECTOR, "#requisitionContainer ul li a")
            link = current_links[i]
            
            row = link.find_element(By.XPATH, "./ancestor::tr")
            cells = row.find_elements(By.TAG_NAME, "td")
            
            row_data = {
                "job_id": link.text.strip(),
                "facility": cells[0].text.split('\n')[0],
                "job_title": cells[2].text.strip(),
                "specialty": cells[1].text.replace('\n', ' | ')
            }
            
            driver.execute_script("arguments[0].click();", link)
            row_data.update(scrape_modal_details())
            scraped_data.append(row_data)
            print(f"   [+] {row_data['job_id']}")

        # Pagination
        try:
            next_btn = driver.find_elements(By.XPATH, f"//a[@class='step' and text()='{current_page + 1}']")
            if next_btn:
                driver.execute_script("arguments[0].click();", next_btn[0])
                current_page += 1
                time.sleep(5)
            else: break
        except: break

    # 4. POSTGRES SYNC
    if scraped_data:
        print(f"Syncing {len(scraped_data)} items...")
        df = pd.DataFrame(scraped_data)
        df.to_sql('hwl_staging', engine, if_exists='replace', index=False)
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO hwl (job_id, facility, job_title, specialty)
                SELECT job_id, facility, job_title, specialty FROM hwl_staging
                ON CONFLICT (job_id) DO UPDATE SET
                    facility = EXCLUDED.facility, job_title = EXCLUDED.job_title, specialty = EXCLUDED.specialty;
                DELETE FROM hwl WHERE job_id NOT IN (SELECT job_id FROM hwl_staging);
                DROP TABLE hwl_staging;
            """))
        print("Success.")

except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
finally:
    driver.quit()
