import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Database Configuration ---
DB_CONFIG = {
    "dbname": "jobboard",
    "user": "development",
    "password": "PATTERNS@123",
    "host": "localhost",
    "port": "5432"
}

# --- Scraper Configuration ---
USERNAME = "am@patternshiring.com"
PASSWORD = "Patterns@2026"
LOGIN_URL = "https://westwaysstaffing.securedportals.com/VMS/vms_supplier_login.aspx"
HOME_URL = "https://westwaysstaffing.securedportals.com/VMS/home-vms-supplier.aspx"

def get_driver():
    """Initializes a fresh Edge driver session."""
    edge_options = Options()
    driver = webdriver.Edge(options=edge_options)
    return driver

def save_to_postgres(client_id, client_name, job_list):
    """Saves jobs to DB. Updates if exists, deletes if not in current scrape list."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        active_job_ids = []

        for job_str in job_list:
            parts = [p.strip() for p in job_str.split('|')]
            if len(parts) < 12: continue # Ensure row has enough data
            
            job_id = parts[0]
            active_job_ids.append(job_id)

            # UPSERT: Insert or Update if job_id exists
            cur.execute("""
                INSERT INTO westway (
                    job_id, company_id, company_name, status, opened, 
                    start_date, end_date, position, department, qty, job_type, last_updated
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (job_id) 
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    opened = EXCLUDED.opened,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    position = EXCLUDED.position,
                    department = EXCLUDED.department,
                    qty = EXCLUDED.qty,
                    job_type = EXCLUDED.job_type,
                    last_updated = CURRENT_TIMESTAMP;
            """, (job_id, client_id, client_name, parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], int(parts[7]), parts[11]))

        # DELETE: Remove jobs for this company that are no longer present in this specific scrape
        if active_job_ids:
            cur.execute("""
                DELETE FROM westway 
                WHERE company_id = %s AND job_id NOT IN %s
            """, (client_id, tuple(active_job_ids)))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"      [Database] Successfully synced {len(active_job_ids)} jobs.")
    except Exception as e:
        print(f"      [Database Error] {e}")

def scrape_jobs(driver, wait):
    """Navigates to the job table and scrapes the data."""
    try:
        # Navigate to orders
        job_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='btn_job_order']/a")))
        job_menu.click()
        open_jobs = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='vms-supplier-open-joborders.aspx']")))
        open_jobs.click()
        
        # Scrape table
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = driver.find_elements(By.XPATH, "//table//tr[td]")
        return [" | ".join([c.text.strip() for c in r.find_elements(By.TAG_NAME, "td") if c.text.strip()]) for r in rows]
    except Exception as e:
        print(f"      [!] Scrape error: {e}")
        return []

# --- Step 1: Initial Fetch to get the list of clients ---
client_names = []
print("Initializing session to fetch master client list...")
initial_driver = get_driver()
initial_wait = WebDriverWait(initial_driver, 20)

try:
    initial_driver.get(LOGIN_URL)
    initial_wait.until(EC.presence_of_element_located((By.ID, "user_name"))).send_keys(USERNAME)
    initial_driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
    initial_driver.find_element(By.ID, "btnLogin").click()

    client_input = initial_wait.until(EC.element_to_be_clickable((By.ID, "tags")))
    client_input.click()
    client_input.send_keys("a")
    initial_wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-autocomplete")))
    time.sleep(2)
    
    dropdown_items = initial_driver.find_elements(By.XPATH, "//ul[contains(@class, 'ui-autocomplete')]//li/a")
    client_names = [item.get_attribute("innerText").strip() for item in dropdown_items if item.get_attribute("innerText").strip()]
    print(f"Found {len(client_names)} clients. Closing initial session.\n")
finally:
    initial_driver.quit()

# --- Step 2: Loop through each client with a fresh browser session ---
for name in client_names:
    print(f"===> Processing: {name}")
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    
    try:
        # Login
        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.ID, "user_name"))).send_keys(USERNAME)
        driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
        driver.find_element(By.ID, "btnLogin").click()

        # Selection Logic
        client_input = wait.until(EC.element_to_be_clickable((By.ID, "tags")))
        client_input.click()
        client_input.send_keys(Keys.CONTROL + "a")
        client_input.send_keys(Keys.BACKSPACE)
        
        search_term = name.split(" - ")[0] if " - " in name else name[:8]
        client_input.send_keys(search_term)
        
        # Select from dropdown
        suggestion_xpath = f"//ul[contains(@class, 'ui-autocomplete')]//li/a[contains(., '{name}')]"
        suggestion = wait.until(EC.visibility_of_element_located((By.XPATH, suggestion_xpath)))
        suggestion.click()
        
        # Click Continue
        continue_btn = driver.find_element(By.ID, "btnClient")
        driver.execute_script("arguments[0].click();", continue_btn)
        
        # Scrape data
        time.sleep(2)
        jobs = scrape_jobs(driver, wait)
        
        # SKIP LOGIC: If no jobs found, move to next client
        if not jobs:
            print(f"      [!] No jobs found for {name}. Skipping DB sync.")
            continue
            
        print(f"      Done. Found {len(jobs)} jobs.")
        
        # Database Logic
        c_id = name.split(" - ")[0] if " - " in name else "Unknown"
        c_name = name.split(" - ")[1] if " - " in name else name
        save_to_postgres(c_id, c_name, jobs)

    except Exception as e:
        print(f"      [!] Error processing {name}: {e}")
    finally:
        driver.quit()

print("All processing finished.")
