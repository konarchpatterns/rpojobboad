import time
import psycopg2
from psycopg2 import sql
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
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

# --- Scraping Configuration ---
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Patterns@25"
LOGIN_URL = "https://www.fieldglass.net/desktop.do"
DASHBOARD_URL = "https://www.us.fieldglass.cloud.sap/my_jp_dashboard.do?cf=1"

options = Options()
options.add_argument("--start-maximized")
options.page_load_strategy = 'eager' 

driver = webdriver.Edge(options=options)
driver.set_page_load_timeout(300) 

def get_text_safe(xpath, wait_time=15):
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text.strip()
    except:
        return "N/A"

def save_to_db(job_data):
    """Handles the UPSERT logic in PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        upsert_query = """
        INSERT INTO fieldglass_jobs (job_id, title, status, bill_rate, site, updated_at)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (job_id) 
        DO UPDATE SET 
            title = EXCLUDED.title,
            status = EXCLUDED.status,
            bill_rate = EXCLUDED.bill_rate,
            site = EXCLUDED.site,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        cur.execute(upsert_query, (
            job_data['job_id'], 
            job_data['title'], 
            job_data['status'], 
            job_data['bill_rate'], 
            job_data['site']
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully synced {job_data['job_id']} to database.")
    except Exception as e:
        print(f"Database error for {job_data['job_id']}: {e}")

try:
    # 1. Login Logic
    print("Opening Fieldglass...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 60) 
    
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "truste-consent-button"))).click()
        print("Cookies accepted.")
    except: pass

    print("Entering credentials...")
    wait.until(EC.visibility_of_element_located((By.ID, "usernameId_new"))).send_keys(USERNAME)
    driver.find_element(By.ID, "passwordId_new").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button.formLoginButton_new").click()

    # 2. Navigate to Dashboard
    print("Navigating to Dashboard...")
    wait.until(EC.url_contains("fieldglass.cloud.sap"))
    
    try:
        driver.get(DASHBOARD_URL)
    except TimeoutException:
        driver.execute_script("window.stop();")

    print("Waiting for dashboard sidebar to load...")
    wait.until(EC.presence_of_element_located((By.ID, "scrollList")))
    time.sleep(5) 

    # 3. Collect Unique Job IDs
    job_urls = {}
    sidebar_items = driver.find_elements(By.CSS_SELECTOR, "ul#scrollList li.listWrap")
    
    for item in sidebar_items:
        try:
            job_id_elem = item.find_element(By.CSS_SELECTOR, "div.grayLabel[title^='UHSJP']")
            job_id = job_id_elem.get_attribute("title")
            driver.execute_script("arguments[0].click();", item)
            time.sleep(2)
            detail_link_elem = driver.find_element(By.CSS_SELECTOR, "div.FGBreadcrumb a")
            href = detail_link_elem.get_attribute("href")
            
            if job_id and href:
                job_urls[job_id] = href
        except Exception:
            continue

    print(f"\nTotal Unique Jobs to Scrape: {len(job_urls)}")

    # 4. Detail Extraction Phase
    for job_id, url in job_urls.items():
        print(f"\n--- Scraping Detail: {job_id} ---")
        try:
            driver.get(url)
        except TimeoutException:
            driver.execute_script("window.stop();")
        
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "badgeWrapper")))
            time.sleep(3) 
            
            title = get_text_safe("//h1[contains(@class, 'fgTitleStyle')]")
            status = get_text_safe("//li[@data-help-id='LABEL_STATUS_40']//div[@class='values']")
            site = get_text_safe("//tr[@id='site']/td")
            bill_rate = get_text_safe("//th[contains(text(), 'Bill Rate')]/following-sibling::td[contains(@class, 'numericFieldBold')]")

            job_entry = {
                'job_id': job_id,
                'title': title,
                'status': status,
                'bill_rate': bill_rate,
                'site': site
            }

            # Save/Update in Database
            save_to_db(job_entry)

        except Exception:
            print(f"Error loading detail page for {job_id}")

except Exception as e:
    print(f"Critical error: {e}")

finally:
    print("\nProcess finished. Closing browser...")
    time.sleep(5)
    driver.quit()
