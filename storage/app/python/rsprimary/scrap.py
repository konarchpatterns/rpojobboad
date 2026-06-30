import time
import pandas as pd
import re
import urllib.parse
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# --- CONFIG ---
PORTAL_URL = "https://saintfrancis.vndly.com/sign_in"
JOBS_URL = "https://saintfrancis.vndly.com/jobs?status=Active%2COn%20Hold%2CPending%2CRejected"
USERNAME = "joyson.bejoy@patternshiring.com"
PASSWORD = "Patterns@123"

# --- DATABASE CONFIG ---
DB_USER = "development"
DB_PASS = "PATTERNS@123" # Password with @ handled below
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "jobboard"

# Encode password to handle the '@' symbol
encoded_pass = urllib.parse.quote_plus(DB_PASS)
engine = create_engine(f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)

def scrape_current_page():
    js_extract = """
    let results = [];
    let items = document.querySelectorAll('[data-testid="items-list-item"]');
    items.forEach(item => {
        let titleLink = item.querySelector('a[href*="/jobs/"]');
        let url = titleLink ? titleLink.href : "";
        let content = item.innerText.replace(/\\n/g, " | ");
        results.push({ "url": url, "raw": content, "title": titleLink ? titleLink.innerText.trim() : "" });
    });
    return results;
    """
    return driver.execute_script(js_extract)

try:
    print(f"Navigating to: {PORTAL_URL}")
    driver.get(PORTAL_URL)
    wait = WebDriverWait(driver, 30)

    # --- LOGIN ---
    user_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input")))
    user_field.click()
    actions = ActionChains(driver)
    actions.move_to_element(user_field).click().send_keys(Keys.CONTROL + "a").send_keys(Keys.BACKSPACE).send_keys(USERNAME).perform()
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[contains(., 'Continue')]").click()

    pass_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
    actions.move_to_element(pass_field).click().send_keys(PASSWORD).perform()
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Sign In')]").click()

    # --- PAGINATION LOOP ---
    time.sleep(10)
    driver.get(JOBS_URL)
    
    all_raw_data = []
    page_number = 1

    while True:
        print(f"Scraping Page {page_number}...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="items-list-item"]')))
        time.sleep(5) 
        
        all_raw_data.extend(scrape_current_page())

        try:
            next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next page'] | //button[contains(., 'Next')]")
            if next_button.is_enabled() and next_button.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                page_number += 1
                time.sleep(8)
            else:
                break
        except:
            break

    # --- PARSING DATA ---
    parsed_jobs = []
    for entry in all_raw_data:
        job_id_match = re.search(r'/(\d+)/?$', entry['url'])
        job_id = job_id_match.group(1) if job_id_match else None
        if not job_id: continue 
        
        parts = [p.strip() for p in entry['raw'].split('|') if p.strip()]
        parsed_jobs.append({
            "job_id": str(job_id),
            "position": entry['title'],
            "status": parts[1] if len(parts) > 1 else "N/A",
            "applicants": parts[2] if len(parts) > 2 else "N/A",
            "pay_rate": parts[6] if len(parts) > 6 else "N/A",
            "location": parts[10] if len(parts) > 10 else "N/A"
        })

    # --- POSTGRESQL SYNC (UPSERT + DELETE) ---
    if parsed_jobs:
        df_new = pd.DataFrame(parsed_jobs).drop_duplicates(subset=['job_id'])
        
        with engine.begin() as conn:
            # 1. Ensure table exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS saint_francis_jobs (
                    job_id TEXT PRIMARY KEY,
                    position TEXT,
                    status TEXT,
                    applicants TEXT,
                    pay_rate TEXT,
                    location TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # 2. Push live scrape to temporary staging table
            df_new.to_sql("temp_sf_scrape", conn, if_exists="replace", index=False)

            # 3. UPSERT: Update if exists, Insert if new
            upsert_query = text("""
                INSERT INTO saint_francis_jobs (job_id, position, status, applicants, pay_rate, location)
                SELECT job_id, position, status, applicants, pay_rate, location FROM temp_sf_scrape
                ON CONFLICT (job_id) DO UPDATE SET
                    position = EXCLUDED.position,
                    status = EXCLUDED.status,
                    applicants = EXCLUDED.applicants,
                    pay_rate = EXCLUDED.pay_rate,
                    location = EXCLUDED.location,
                    last_updated = CURRENT_TIMESTAMP;
            """)
            conn.execute(upsert_query)

            # 4. REMOVE: Delete jobs that are no longer in the live scrape
            delete_query = text("""
                DELETE FROM saint_francis_jobs 
                WHERE job_id NOT IN (SELECT job_id FROM temp_sf_scrape);
            """)
            deleted_count = conn.execute(delete_query).rowcount
            
            # Cleanup
            conn.execute(text("DROP TABLE IF EXISTS temp_sf_scrape;"))

        print(f"Database Sync Success: {len(df_new)} live jobs synced. {deleted_count} expired jobs removed.")
    else:
        print("No jobs were found to scrape.")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()