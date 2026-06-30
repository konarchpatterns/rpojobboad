import time
import pandas as pd
import psycopg2
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. CONFIGURATION ---
DB_CONFIG = {
    "dbname": "jobboard",
    "user": "development",
    "password": "PATTERNS@123",
    "host": "localhost",
    "port": "5432"
}

LOGIN_URL = "https://trio.triovms.com/Agency/LocumsDashboard"
DATA_URL = "https://trio.triovms.com/LocumOrder/Index/Open"
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Recruit@123"

# --- 2. DATABASE LOGIC ---
def sync_to_postgres(jobs_dict):
    """Handles UPSERT and Cleanup for the TrioVMS data."""
    if not jobs_dict:
        print("No data to sync.")
        return

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get all Job IDs from the current scrape to handle deletions later
        scraped_job_ids = list(jobs_dict.keys())

        for job_id, data in jobs_dict.items():
            # UPSERT Logic
            cur.execute("""
                INSERT INTO trovms (
                    job_id, status, reason, job_type, profession, 
                    specialty, facility, city, state, start_date, bid_due_date, last_updated
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (job_id) 
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    reason = EXCLUDED.reason,
                    last_updated = CURRENT_TIMESTAMP;
            """, (
                job_id, data['Status'], data['Reason'], data['Type'], 
                data['Profession'], data['Specialty'], data['Facility'], 
                data['City'], data['State'], data['Start'], data['Bid Due Date']
            ))

        # DELETE Logic: Remove jobs in DB that were NOT found in this scrape
        if scraped_job_ids:
            cur.execute("DELETE FROM trovms WHERE job_id NOT IN %s", (tuple(scraped_job_ids),))

        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully synced {len(scraped_job_ids)} jobs to PostgreSQL.")
    except Exception as e:
        print(f"Database Error: {e}")

# --- 3. SCRAPING LOGIC ---
edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)

def scrape_visible_rows():
    js_script = """
    let rows = document.querySelectorAll('tr[id*="DXDataRow"]');
    let data = [];
    rows.forEach(row => {
        let cells = row.querySelectorAll('td.dxgv');
        if(cells.length >= 8) {
            let jobId = cells[2].innerText.trim();
            if(jobId && jobId !== "") {
                data.push({
                    "Status": cells[0].innerText.trim(),
                    "Reason": cells[1].innerText.trim(),
                    "Job Id": jobId,
                    "Type": cells[3].innerText.trim(),
                    "Profession": cells[4].innerText.trim(),
                    "Specialty": cells[5].innerText.trim(),
                    "Facility": cells[6].innerText.trim(),
                    "City": cells[7].innerText.trim(),
                    "State": cells[8].innerText.trim(),
                    "Start": cells[9] ? cells[9].innerText.trim() : "",
                    "Bid Due Date": cells[11] ? cells[11].innerText.trim() : ""
                });
            }
        }
    });
    return data;
    """
    return driver.execute_script(js_script)

try:
    print("Navigating to TrioVMS...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 45)

    # Login
    wait.until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait and Navigate to Data
    time.sleep(15) 
    driver.get(DATA_URL)
    
    all_jobs = {} 
    target_total = 297 
    container_selector = "div.dxgvCSD"
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr[id*="DXDataRow"]')))

    attempts_without_new_data = 0
    while len(all_jobs) < target_total and attempts_without_new_data < 20:
        current_batch = scrape_visible_rows()
        initial_count = len(all_jobs)
        
        for job in current_batch:
            all_jobs[job["Job Id"]] = job
        
        new_count = len(all_jobs)
        print(f"Progress: {new_count}/{target_total}")

        if new_count == initial_count:
            attempts_without_new_data += 1
        else:
            attempts_without_new_data = 0

        # Scroll for AJAX load
        driver.execute_script(f"document.querySelector('{container_selector}').scrollTop += 350;")
        time.sleep(2)

    # --- SYNC TO DATABASE ---
    sync_to_postgres(all_jobs)

except Exception as e:
    print(f"Global Error: {e}")
finally:
    driver.quit()
