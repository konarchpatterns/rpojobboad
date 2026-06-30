import psycopg2
from psycopg2.extras import execute_values
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime

# --- Database Configuration ---
DB_CONFIG = {
    "dbname": "jobboard",
    "user": "development",
    "password": "PATTERNS@123",
    "host": "localhost",
    "port": "5432"
}

# --- Selenium Configuration ---
edge_options = Options()
edge_options.add_experimental_option("detach", True)
edge_options.add_argument("--ignore-certificate-errors")
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)

def sync_to_db(scraped_jobs):
    """
    Synchronizes scraped data with PostgreSQL.
    Handles Foreign Key constraints by updating the parent 'westway' table first.
    """
    if not scraped_jobs:
        print("No jobs scraped to sync.")
        return

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Ensure job_id is treated as a string for all operations
        active_ids = [str(job['job_id']) for job in scraped_jobs]

        # 1. Update Parent Table (westway) first to satisfy Foreign Key
        # This prevents the "Key (job_id) is not present in table westway" error
        parent_upsert_query = """
            INSERT INTO public.westway (job_id)
            VALUES %s
            ON CONFLICT (job_id) DO NOTHING;
        """
        parent_data = [(jid,) for jid in active_ids]
        execute_values(cur, parent_upsert_query, parent_data)
        print(f"Ensured {len(parent_data)} job IDs exist in parent table.")
        
        # 2. UPSERT Detail Table
        upsert_query = """
            INSERT INTO public.westway_details (
                job_id, position, status, pay_range, opened, dates, shift_info, description, company_name, last_updated
            ) VALUES %s
            ON CONFLICT (job_id) 
            DO UPDATE SET 
                position = EXCLUDED.position,
                status = EXCLUDED.status,
                pay_range = EXCLUDED.pay_range,
                opened = EXCLUDED.opened,
                dates = EXCLUDED.dates,
                shift_info = EXCLUDED.shift_info,
                description = EXCLUDED.description,
                company_name = EXCLUDED.company_name,
                last_updated = EXCLUDED.last_updated;
        """
        
        data_tuples = [
            (
                str(j['job_id']), j['position'], j['status'], j['pay_range'], 
                j['opened'], j['dates'], j['shift_info'], j['description'], 
                j['company_name'], datetime.now()
            ) for j in scraped_jobs
        ]
        
        execute_values(cur, upsert_query, data_tuples)
        print(f"Successfully upserted {len(data_tuples)} job details.")

        # 3. DELETE stale records (Optional: Clean up both tables)
        if active_ids:
            # Delete details first because of the FK dependency
            cur.execute("DELETE FROM public.westway_details WHERE job_id NOT IN %s", (tuple(active_ids),))
            # Then delete from parent table
            cur.execute("DELETE FROM public.westway WHERE job_id NOT IN %s", (tuple(active_ids),))
            print(f"Purged closed jobs from database.")

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database Sync Error: {e}")

def get_list_from_dropdown():
    print("Triggering dropdown to extract supplier list...")
    client_input = wait.until(EC.element_to_be_clickable((By.ID, "tags")))
    client_input.click()
    client_input.send_keys(Keys.ARROW_DOWN)
    time.sleep(2) 

    items = driver.find_elements(By.CSS_SELECTOR, ".ui-menu-item")
    suppliers = [item.text for item in items if item.text.strip() != ""]
    print(f"Detected {len(suppliers)} suppliers.")
    return suppliers

def switch_supplier(supplier_name):
    driver.get("https://westwaysstaffing.securedportals.com/VMS/home-vms-supplier.aspx")
    wait.until(EC.element_to_be_clickable((By.ID, "tags")))
    
    script = f"document.getElementById('customer').value = '{supplier_name}'; __doPostBack('ClientLookup$customer', '');"
    driver.execute_script(script)
    
    # Wait for visual confirmation
    wait.until(EC.text_to_be_present_in_element((By.ID, "ClientLookup_lblClient"), supplier_name.split('-')[0].strip()))

def scrape_jobs(supplier_name):
    jobs_list = []
    job_card = wait.until(EC.visibility_of_element_located((By.ID, "btn_job_order")))
    actions.move_to_element(job_card).perform()
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='vms-supplier-open-joborders.aspx']"))).click()

    selector = "//a[contains(@class, 'viewdetail') and text()='Candidates']"
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, selector)))
    except:
        return []

    count = len(driver.find_elements(By.XPATH, selector))
    for i in range(count):
        btns = driver.find_elements(By.XPATH, selector)
        job_id = str(btns[i].get_attribute("data-job")) # Ensure string conversion here
        
        driver.execute_script("arguments[0].click();", btns[i])
        wait.until(EC.presence_of_element_located((By.ID, "hdrStatus")))
        time.sleep(1)

        job_data = {
            'job_id': job_id,
            'status': driver.find_element(By.ID, "hdrStatus").text.split(':')[-1].strip(),
            'dates': driver.find_element(By.ID, "hdrDates").text.split(':')[-1].strip(),
            'opened': driver.find_element(By.ID, "hdrOpened").text.split(':')[-1].strip(),
            'shift_info': driver.find_element(By.ID, "hdrTimes").text.split(':')[-1].strip(),
            'position': driver.find_element(By.ID, "hdrPosition").text.split(':')[-1].strip(),
            'description': driver.find_element(By.ID, "hdrDescr").text.replace('Description:', '').strip(),
            'pay_range': driver.find_element(By.ID, "hdrPay").text.split(':')[-1].strip(),
            'company_name': supplier_name
        }
        jobs_list.append(job_data)
        
        driver.back()
        wait.until(EC.presence_of_element_located((By.XPATH, selector)))
    
    return jobs_list

def main():
    all_master_data = []
    try:
        driver.get("https://westwaysstaffing.securedportals.com/VMS/vms_supplier_login.aspx")
        wait.until(EC.presence_of_element_located((By.ID, "user_name"))).send_keys("am@patternshiring.com")
        driver.find_element(By.ID, "user_pass").send_keys("Patterns@2026")
        driver.find_element(By.ID, "btnLogin").click()

        suppliers = get_list_from_dropdown()
        
        for s in suppliers:
            try:
                switch_supplier(s)
                supplier_jobs = scrape_jobs(s)
                all_master_data.extend(supplier_jobs)
                print(f"Scraped {len(supplier_jobs)} jobs from {s}")
            except Exception as e:
                print(f"Error processing {s}: {e}")

        sync_to_db(all_master_data)

    finally:
        print("Process complete.")
        driver.quit()

if __name__ == "__main__":
    main()