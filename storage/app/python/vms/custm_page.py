import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- CONFIGURATION ---
LOGIN_URL = "https://vms.laboredge.com/signin"
DATA_URL = "https://vms.laboredge.com/supplier/jobs/view/alljobs"
USERNAME = "pooja.raut@patternshiring.com"
PASSWORD = "Patterns@123"
ORG_CODE = "NS"
TARGET_PAGE = 6 

DB_CONFIG = {
    "dbname": "jobboard",
    "user": "development",
    "password": "PATTERNS@123",
    "host": "localhost",
    "port": "5432"
}

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.init_db()
    def get_connection(self):
        return psycopg2.connect(**self.config)
    def init_db(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS laboredge_job_details (
                id SERIAL PRIMARY KEY, job_id TEXT UNIQUE, facility TEXT,
                status TEXT, profession TEXT, specialty TEXT, start_date TEXT,
                end_date TEXT, bill_rate TEXT, description TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    def save_job(self, data):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            query = """
                INSERT INTO laboredge_job_details (job_id, facility, status, profession, specialty, start_date, end_date, bill_rate, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO UPDATE SET status = EXCLUDED.status, bill_rate = EXCLUDED.bill_rate, scraped_at = CURRENT_TIMESTAMP;
            """
            cur.execute(query, (data['job_id'], data['facility'], data['status'], data['profession'], data['specialty'], data['start_date'], data['end_date'], data['bill_rate'], data['description']))
            conn.commit()
            cur.close()
            conn.close()
            print(f"   [DB] Saved Job ID: {data['job_id']}")
        except Exception as e: print(f"   [DB ERROR] {e}")

# --- SELENIUM SETUP ---
edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 15)
db = DatabaseManager(DB_CONFIG)

def scrape_detail_page():
    try:
        # Wait for Job ID to appear
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "[formcontrolname='jobId']").get_attribute("value").strip() != "")
        time.sleep(2)
        
        def get_input_val(selector):
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                return el.get_attribute("value") or el.get_attribute("textContent")
            except: return "N/A"
            
        def get_dropdown_val(form_control):
            try:
                path = f"//p-custom-dropdown[@formcontrolname='{form_control}']//span[contains(@class, 'p-select-label')]"
                return driver.find_element(By.XPATH, path).get_attribute("textContent").strip()
            except: return "N/A"

        job_data = {
            "job_id": get_input_val("[formcontrolname='jobId']"),
            "facility": get_input_val("[formcontrolname='clientName']"),
            "status": get_dropdown_val("jobStatusId"),
            "profession": get_dropdown_val("professionId"),
            "specialty": get_dropdown_val("specialtyId"),
            "start_date": get_input_val("[formcontrolname='startDate'] input"),
            "end_date": get_input_val("[formcontrolname='endDate'] input"),
            "bill_rate": "N/A", "description": "N/A"
        }
        
        try: job_data["bill_rate"] = driver.find_element(By.CSS_SELECTOR, "p-table input.p-filled").get_attribute("value")
        except: pass
        
        try:
            iframes = driver.find_elements(By.CSS_SELECTOR, "editor[formcontrolname='jobDescription'] iframe")
            if iframes:
                driver.switch_to.frame(iframes[0])
                job_data["description"] = driver.find_element(By.TAG_NAME, "body").text.strip()
                driver.switch_to.default_content()
        except: driver.switch_to.default_content()
        
        return job_data
    except:
        driver.switch_to.default_content()
        return None

try:
    print("Logging into LaborEdge...")
    driver.get(LOGIN_URL)
    wait.until(EC.element_to_be_clickable((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "organizationCode").send_keys(ORG_CODE)
    login_btn = driver.find_element(By.XPATH, "//span[text()='LOGIN']/ancestor::button")
    driver.execute_script("arguments[0].click();", login_btn)

    print("Navigating to Jobs Table...")
    time.sleep(10)
    driver.get(DATA_URL)
    
    # --- NAVIGATION TO PAGE 6 ---
    print(f"Moving to Page {TARGET_PAGE}...")
    while True:
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "new-custom-paginator")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check if current page is 6
            active_xpath = f"//span[contains(@class, 'paginator-button') and contains(@class, 'active')]//span[text()='{TARGET_PAGE}']"
            if driver.find_elements(By.XPATH, active_xpath):
                print(f"Confirmed: On Page {TARGET_PAGE}.")
                break
                
            # Try clicking number 6 directly
            page_xpath = f"//span[contains(@class, 'paginator-button')]//span[text()='{TARGET_PAGE}']"
            try:
                page_btn = driver.find_element(By.XPATH, page_xpath)
                driver.execute_script("arguments[0].click();", page_btn)
                time.sleep(5)
            except NoSuchElementException:
                # Click 'Next' Arrow
                next_btn = driver.find_element(By.CSS_SELECTOR, "p-button[icon='pi pi-angle-right'] button")
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(5)
        except Exception:
            time.sleep(2)

    # --- SCRAPING PROCESS ---
    print(f"--- Starting Scrape on Page {TARGET_PAGE} ---")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-datatable-tbody")))
    
    # Count rows
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.p-datatable-selectable-row")
    total_rows = len(rows)
    print(f"Found {total_rows} jobs.")

    for i in range(total_rows):
        try:
            # Re-locate rows to handle back navigation
            current_rows = driver.find_elements(By.CSS_SELECTOR, "tr.p-datatable-selectable-row")
            row = current_rows[i]
            
            # Scroll row to middle of screen
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
            time.sleep(1)
            
            # --- HOVER & CLICK SEQUENCE ---
            actions = ActionChains(driver)
            
            # 1. Hover over the 3 dots
            dots_icon = row.find_element(By.CSS_SELECTOR, "i.icon-dots")
            actions.move_to_element(dots_icon).perform()
            time.sleep(0.5)
            
            # 2. Click the dots icon
            actions.click(dots_icon).perform()
            
            # 3. Wait for and click "View Job Details"
            detail_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'View Job Details')]"))
            )
            actions.move_to_element(detail_link).click().perform()

            # 4. Scrape the data
            job_details = scrape_detail_page()
            if job_details:
                db.save_job(job_details)
            
            # 5. Return to list
            driver.back()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-datatable-tbody")))
            time.sleep(5) # Let table reload
            
        except Exception as e:
            print(f"Skipping Row {i}: Element might be blocked or missing.")
            # Click background to close any open menus
            try: driver.execute_script("document.body.click();")
            except: pass
            continue

except Exception as e:
    print(f"Fatal Error: {e}")
finally:
    print("Process finished.")
    driver.quit()