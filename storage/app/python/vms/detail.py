import time
import psycopg2
from psycopg2 import sql
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- CONFIGURATION ---
LOGIN_URL = "https://vms.laboredge.com/signin"
DATA_URL = "https://vms.laboredge.com/supplier/jobs/view/alljobs"
USERNAME = "pooja.raut@patternshiring.com"
PASSWORD = "Patterns@123"
ORG_CODE = "NS"

# --- POSTGRES CONFIGURATION ---
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
        """Creates the table if it doesn't exist."""
        conn = self.get_connection()
        cur = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS laboredge_job_details (
            id SERIAL PRIMARY KEY,
            job_id TEXT UNIQUE,
            facility TEXT,
            status TEXT,
            profession TEXT,
            specialty TEXT,
            start_date TEXT,
            end_date TEXT,
            bill_rate TEXT,
            description TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        cur.close()
        conn.close()

    def save_job(self, data):
        """Inserts or updates job data."""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            insert_query = """
            INSERT INTO laboredge_job_details (job_id, facility, status, profession, specialty, start_date, end_date, bill_rate, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_id) 
            DO UPDATE SET 
                status = EXCLUDED.status,
                bill_rate = EXCLUDED.bill_rate,
                scraped_at = CURRENT_TIMESTAMP;
            """
            cur.execute(insert_query, (
                data['job_id'], data['facility'], data['status'],
                data['profession'], data['specialty'], data['start_date'],
                data['end_date'], data['bill_rate'], data['description']
            ))
            conn.commit()
            cur.close()
            conn.close()
            print(f"   [DB] Successfully saved Job ID: {data['job_id']}")
        except Exception as e:
            print(f"   [DB ERROR] Could not save to database: {e}")

# --- SELENIUM SETUP ---
edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 30)
db = DatabaseManager(DB_CONFIG)

def scrape_detail_page():
    """Extracts data and returns it as a dictionary."""
    try:
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

        # Collect data into dictionary
        job_data = {
            "job_id": get_input_val("[formcontrolname='jobId']"),
            "facility": get_input_val("[formcontrolname='clientName']"),
            "status": get_dropdown_val("jobStatusId"),
            "profession": get_dropdown_val("professionId"),
            "specialty": get_dropdown_val("specialtyId"),
            "start_date": get_input_val("[formcontrolname='startDate'] input"),
            "end_date": get_input_val("[formcontrolname='endDate'] input"),
            "bill_rate": "N/A",
            "description": "N/A"
        }

        try:
            job_data["bill_rate"] = driver.find_element(By.CSS_SELECTOR, "p-table input.p-filled").get_attribute("value")
        except: pass

        try:
            iframes = driver.find_elements(By.CSS_SELECTOR, "editor[formcontrolname='jobDescription'] iframe")
            if iframes:
                driver.switch_to.frame(iframes[0])
                job_data["description"] = driver.find_element(By.TAG_NAME, "body").text.strip()
                driver.switch_to.default_content()
        except:
            driver.switch_to.default_content()

        print(f"Scraped Job ID: {job_data['job_id']}")
        return job_data

    except Exception as e:
        print(f"      [!] Detail Page Scrape Error: {e}")
        driver.switch_to.default_content()
        return None

try:
    # 1. LOGIN
    print("Logging into LaborEdge...")
    driver.get(LOGIN_URL)
    wait.until(EC.element_to_be_clickable((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "organizationCode").send_keys(ORG_CODE)
    login_btn = driver.find_element(By.XPATH, "//span[text()='LOGIN']/ancestor::button")
    driver.execute_script("arguments[0].click();", login_btn)

    # 2. NAVIGATION
    print("Redirecting to Jobs List...")
    time.sleep(12)
    driver.get(DATA_URL)
    
    current_page = 1
    while True:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-datatable-tbody")))
        time.sleep(5) 

        row_elements = driver.find_elements(By.CSS_SELECTOR, "tr.p-datatable-selectable-row")
        row_count = len(row_elements)
        print(f"--- Page {current_page} | Processing {row_count} rows ---")

        for i in range(row_count):
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, "tr.p-datatable-selectable-row")
                if i >= len(rows): break
                
                row = rows[i]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                time.sleep(1)
                
                menu_dots = row.find_element(By.CSS_SELECTOR, "td.sticky-col i.icon-dots, i.pi-ellipsis-v")
                
                actions = ActionChains(driver)
                actions.move_to_element(menu_dots).perform()
                time.sleep(0.8)
                driver.execute_script("arguments[0].click();", menu_dots)

                detail_xpath = "//span[contains(text(), 'View Job Details')]"
                detail_link = wait.until(EC.visibility_of_element_located((By.XPATH, detail_xpath)))
                actions.move_to_element(detail_link).click().perform()

                # SCRAPE AND SAVE
                job_info = scrape_detail_page()
                if job_info:
                    db.save_job(job_info)
                
                driver.back()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-datatable-tbody")))
                time.sleep(4)

            except Exception as e:
                print(f"Error on row {i}. Recovering list...")
                if "supplier/jobs/view" not in driver.current_url:
                    driver.get(DATA_URL)
                    time.sleep(8)
                continue

        # 3. PAGINATION
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            next_btn_xpath = "//new-custom-paginator//p-button[@icon='pi pi-angle-right']//button"
            next_btn = driver.find_element(By.XPATH, next_btn_xpath)
            
            if next_btn.is_enabled() and "disabled" not in next_btn.get_attribute("class"):
                print(f"Clicking Next Page...")
                driver.execute_script("arguments[0].click();", next_btn)
                current_page += 1
                time.sleep(10)
            else:
                print("Last page reached. Scraping complete.")
                break
        except Exception:
            break

except Exception as fatal_e:
    print(f"Fatal Error: {fatal_e}")
finally:
    print("Closing session...")
    time.sleep(10)
    driver.quit()