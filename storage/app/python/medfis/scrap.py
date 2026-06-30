import time
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
LOGIN_URL = "https://vms.medefis5.com/"
JOBS_URL = "https://vms.medefis5.com/jobs"
USERNAME = "patterns"
PASSWORD = "PHC!#2026$"

# PostgreSQL Configuration
DB_USER = "development"
DB_PASS = urllib.parse.quote_plus("PATTERNS@123")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "jobboard"

# Database Connection Engine
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)

def scrape_react_table():
    js_script = """
    let rows = document.querySelectorAll('.rt-tr-group');
    let data = [];
    rows.forEach(row => {
        let cells = row.querySelectorAll('.rt-td');
        if(cells.length >= 5) {
            let jobId = cells[1].innerText.trim();
            if(jobId) {
                data.push({
                    "job_name": cells[0].innerText.trim(),
                    "job_number": jobId,
                    "facility": cells[2].innerText.trim(),
                    "specialty": cells[3].innerText.trim(),
                    "sub_specialty": cells[4].innerText.trim(),
                    "job_type": cells[5] ? cells[5].innerText.trim() : "N/A",
                    "positions": cells[7] ? cells[7].innerText.trim() : "N/A",
                    "start_date": cells[8] ? cells[8].innerText.trim() : "N/A",
                    "posted_date": cells[9] ? cells[9].innerText.trim() : "N/A"
                });
            }
        }
    });
    return data;
    """
    return driver.execute_script(js_script)

try:
    print("Navigating to Medefis Login...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 45)

    # 1. LOGIN HANDLING
    time.sleep(8)
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(0)

    user_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], #Username")))
    user_input.send_keys(USERNAME)
    pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'], #Password")
    pass_input.send_keys(PASSWORD)

    driver.execute_script("""
        let inputs = document.querySelectorAll('input');
        inputs.forEach(i => {
            i.dispatchEvent(new Event('input', { bubbles: true }));
            i.dispatchEvent(new Event('change', { bubbles: true }));
        });
    """)

    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Login')]")))
    driver.execute_script("arguments[0].removeAttribute('disabled');", login_btn)
    login_btn.click()
    driver.switch_to.default_content()

    # 2. NAVIGATE TO JOBS
    time.sleep(15) 
    driver.get(JOBS_URL)
    
    live_site_data = [] 
    current_page = 1

    # 3. SCRAPE DATA
    while True:
        print(f"Scraping Page {current_page}...")
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rt-tbody")))
            time.sleep(10) 
            
            page_data = scrape_react_table()
            if page_data:
                live_site_data.extend(page_data)
            else:
                break
        except Exception:
            break

        try:
            next_btn = driver.find_elements(By.CSS_SELECTOR, ".-next button")
            if next_btn and not next_btn[0].get_property('disabled'):
                driver.execute_script("arguments[0].click();", next_btn[0])
                current_page += 1
                time.sleep(8)
            else:
                break
        except:
            break

    # 4. DATABASE SYNCHRONIZATION
    if live_site_data:
        df_live = pd.DataFrame(live_site_data).drop_duplicates(subset=['job_number'])
        
        with engine.begin() as conn:
            # Step A: Ensure Table Exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS medefis_jobs (
                    job_name TEXT,
                    job_number TEXT PRIMARY KEY,
                    facility TEXT,
                    specialty TEXT,
                    sub_specialty TEXT,
                    job_type TEXT,
                    positions TEXT,
                    start_date TEXT,
                    posted_date TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Step B: Load to Temporary Staging Table
            df_live.to_sql("temp_jobs_scrape", conn, if_exists="replace", index=False)

            # Step C: UPSERT (Update if exists, Insert if new)
            upsert_query = text("""
                INSERT INTO medefis_jobs (job_name, job_number, facility, specialty, sub_specialty, job_type, positions, start_date, posted_date)
                SELECT job_name, job_number, facility, specialty, sub_specialty, job_type, positions, start_date, posted_date FROM temp_jobs_scrape
                ON CONFLICT (job_number) DO UPDATE SET
                    job_name = EXCLUDED.job_name,
                    facility = EXCLUDED.facility,
                    specialty = EXCLUDED.specialty,
                    sub_specialty = EXCLUDED.sub_specialty,
                    job_type = EXCLUDED.job_type,
                    positions = EXCLUDED.positions,
                    start_date = EXCLUDED.start_date,
                    posted_date = EXCLUDED.posted_date,
                    last_updated = CURRENT_TIMESTAMP;
            """)
            conn.execute(upsert_query)

            # Step D: DELETE (Remove jobs no longer on site)
            delete_query = text("""
                DELETE FROM medefis_jobs 
                WHERE job_number NOT IN (SELECT job_number FROM temp_jobs_scrape);
            """)
            deleted_count = conn.execute(delete_query).rowcount
            
            # Cleanup
            conn.execute(text("DROP TABLE temp_jobs_scrape;"))
            
        print(f"Sync Complete: {len(df_live)} live jobs synced. {deleted_count} expired jobs removed.")
    else:
        print("No data found to sync.")

except Exception as e:
    print(f"Global Error: {e}")
finally:
    driver.quit()