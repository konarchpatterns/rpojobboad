import time
import json
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
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Recruit@123"

# --- 2. DATABASE LOGIC ---
def get_job_ids_from_db():
    """Retrieves all job IDs that need detail scraping."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Querying job_id. You can add 'WHERE description IS NULL' to only scrape new ones.
        cur.execute("SELECT job_id FROM trovms ORDER BY id ASC")
        ids = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return ids
    except Exception as e:
        print(f"Database Read Error: {e}")
        return []

def update_job_details_in_db(job_id, job_data):
    """Updates the database with the scraped description and full JSON data."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        description = job_data.get('Full_Job_Description', '')
        # Convert dictionary to JSON string for Postgres JSONB column
        details_json = json.dumps(job_data)

        cur.execute("""
            UPDATE trovms 
            SET description = %s, 
                details_json = %s,
                last_updated = CURRENT_TIMESTAMP
            WHERE job_id = %s
        """, (description, details_json, job_id))

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database Update Error for {job_id}: {e}")

# --- 3. SCRAPING LOGIC ---
def scrape_job_page(driver, job_id):
    """Navigates to the dynamic job page and extracts panel and table data."""
    detail_url = f"https://trio.triovms.com/Agency/Job/{job_id}"
    print(f"\n[>>>] Scraping Job: {job_id}")
    
    try:
        driver.get(detail_url)
        wait = WebDriverWait(driver, 15)
        # Wait for the panel body to be present
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "panel-body")))
        time.sleep(1) # Stability buffer

        js_extract = """
        let results = {};

        // 1. Extract Sectional Text (Submission Requirements, About Facility, etc.)
        let sections = document.querySelectorAll('.panel-body h6');
        sections.forEach(header => {
            let title = header.innerText.trim();
            let content = header.nextElementSibling;
            if (content) {
                results[title] = content.innerText.trim();
            }
        });

        // 2. Extract Main Job Description (The Dates, Rates, and specific Job Details)
        let mainDesc = document.querySelector('.panel-body .ml-15 span');
        if (mainDesc) {
            results['Full_Job_Description'] = mainDesc.innerText.trim();
        }

        // 3. Extract Additional Facility Info Table
        let tableRows = document.querySelectorAll('.table-form tr');
        tableRows.forEach(row => {
            let cells = row.querySelectorAll('td');
            cells.forEach(cell => {
                let labelEl = cell.querySelector('.text-muted');
                if (labelEl) {
                    let label = labelEl.innerText.trim();
                    // Extract text while excluding the label text itself
                    let value = cell.innerText.replace(label, '').trim();
                    results[label] = value;
                }
            });
        });

        return results;
        """
        data = driver.execute_script(js_extract)
        return data

    except Exception as e:
        print(f"  [!] Error on {job_id}: {e}")
        return None

# --- 4. MAIN EXECUTION ---
edge_options = Options()
edge_options.add_argument("--start-maximized")
# Optimization: prevent browser noise
edge_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

driver = webdriver.Edge(options=edge_options)

try:
    # A. Perform Login
    print("Logging into TrioVMS...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Wait for dashboard redirect
    time.sleep(10)

    # B. Fetch IDs from DB
    job_ids = get_job_ids_from_db()
    print(f"Loaded {len(job_ids)} jobs from database.")

    # C. Loop and Scrape
    for count, j_id in enumerate(job_ids, 1):
        job_data = scrape_job_page(driver, j_id)
        
        if job_data:
            # Print a summary to console
            print(f"  Facility: {job_data.get('Facility', 'N/A')}")
            print(f"  Address: {job_data.get('Address', 'N/A')}")
            
            # Save back to database
            update_job_details_in_db(j_id, job_data)
            print(f"  [OK] Updated DB for {j_id} ({count}/{len(job_ids)})")
        
        # Politeness delay to prevent rate-limiting
        time.sleep(2)

except Exception as e:
    print(f"Global Error: {e}")
finally:
    print("Closing browser...")
    driver.quit()