import time
import json
import urllib.parse
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
LOGIN_URL = "https://vms.medefis5.com/"
BASE_DETAIL_URL = "https://vms.medefis5.com/jobs/"
USERNAME = "patterns"
PASSWORD = "PHC!#2026$"

# PostgreSQL Configuration
DB_USER = "development"
DB_PASS = urllib.parse.quote_plus("PATTERNS@123")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "jobboard"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# EDGE OPTIONS (Optimized for stability)
edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_argument("--disable-smart-screen")
edge_options.add_argument("--dns-prefetch-disable")
edge_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 25)

def get_job_numbers_from_db():
    """Fetches all job numbers already present in your database."""
    print("Fetching job numbers from PostgreSQL...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT job_number FROM medefis_jobs"))
        return [row[0] for row in result]

def scrape_detail_page(job_number):
    """Navigates to the URL and extracts all detail fields."""
    driver.get(f"{BASE_DETAIL_URL}{job_number}")
    try:
        # Wait for labels to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-label")))
        time.sleep(4) # Buffer for React content hydration

        js_extract = """
        let data = {};
        document.querySelectorAll('.Row__LayoutRow-sc-1v07ltz-0.codcwM.row').forEach(row => {
            let label = row.querySelector('label');
            let value = row.querySelector('div[class*="Column-sc"]'); 
            if (label && value) {
                let key = label.innerText.replace(':', '').trim();
                let val = value.innerText.trim();
                if(key) data[key] = val;
            }
        });
        
        let desc = document.querySelector('.Wrapper-no2vrf-0.inNkoq p');
        if(desc) data['Job Description Text'] = desc.innerText.trim();
        
        return data;
        """
        return driver.execute_script(js_extract)
    except Exception as e:
        print(f"   ⚠️ Error loading page for {job_number}: {e}")
        return None

def update_db_json(job_number, details):
    """Updates the details_json column for the specific job_number."""
    with engine.begin() as conn:
        update_query = text("""
            UPDATE medefis_jobs 
            SET details_json = :json_data, 
                last_updated = CURRENT_TIMESTAMP
            WHERE job_number = :num
        """)
        conn.execute(update_query, {
            "num": job_number,
            "json_data": json.dumps(details)
        })

# --- EXECUTION ---
try:
    # 1. Fetch Job IDs from your existing DB table
    job_list = get_job_numbers_from_db()
    
    if not job_list:
        print("No jobs found in the database. Please ensure 'medefis_jobs' is populated.")
    else:
        print(f"Found {len(job_list)} jobs in database. Starting login...")

        # 2. LOGIN (Required to access detail pages)
        driver.get(LOGIN_URL)
        time.sleep(5)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes: driver.switch_to.frame(0)
        
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], #Username"))).send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, "input[type='password'], #Password").send_keys(PASSWORD)
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Login')]")))
        driver.execute_script("arguments[0].click();", login_btn)
        driver.switch_to.default_content()
        
        print("Step 2 complete. Starting deep-scrape of individual URLs...")
        time.sleep(5) # Delay to ensure login session is active

        # 3. ITERATE THROUGH DATABASE IDS
        for i, jid in enumerate(job_list, 1):
            print(f"[{i}/{len(job_list)}] Scrapping Job #{jid}...")
            
            detail_data = scrape_detail_page(jid)
            if detail_data:
                update_db_json(jid, detail_data)
                # Print sample info to terminal for monitoring
                print(f"   ✅ Updated: {detail_data.get('Job Status', 'N/A')} | Rate: {detail_data.get('Facility Rate', 'N/A')}")
            
            # 2 second delay to prevent SmartScreen/DNS errors seen in your terminal
            time.sleep(2)

    print("\n--- Process Complete: Database Updated ---")

except Exception as e:
    print(f"\nCritical Global Error: {e}")
finally:
    driver.quit()