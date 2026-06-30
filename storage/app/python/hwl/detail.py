import time
import json
import psycopg2
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
DB_CONFIG = {
    "dbname": "jobboard",
    "user": "development",
    "password": "PATTERNS@123",
    "host": "localhost",
    "port": "5432"
}

LOGIN_URL = "https://vms.hwlmsp.com/shiftrock/user/login"
DATA_URL = "https://vms.hwlmsp.com/shiftrock/requisitionLocum/agencyLocumRequisition"
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Windows#1"

edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_argument("--disable-blink-features=AutomationControlled")
edge_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 20)

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hwl_details (
            job_id TEXT PRIMARY KEY,
            address TEXT,
            shift TEXT,
            weeks TEXT,
            pay_rates JSONB,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    return conn, cur

def scrape_rates_modal():
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "rateTableElement")))
        time.sleep(1) 
        rates = {}
        rows = driver.find_elements(By.CSS_SELECTOR, "#rateTableElement tr.rateTableRowPropose")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                shift_name = cells[0].text.strip()
                try:
                    rate_val = cells[1].find_element(By.CSS_SELECTOR, "input.fixed-rate-input").get_attribute("value")
                    if shift_name: rates[shift_name] = rate_val
                except: continue
        
        close_btn = driver.find_element(By.ID, "closeRatePopup")
        driver.execute_script("arguments[0].click();", close_btn)
        # Wait for modal to be completely gone
        wait.until(EC.invisibility_of_element_located((By.ID, "rateTableElement")))
        return rates
    except: return {}

def scrape_modal_details():
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "viewReqModalContent")))
        time.sleep(1) 
        def find_val(label_text):
            try:
                path = f"//div[contains(@class, 'req-details-div-label') and contains(., '{label_text}')]/following-sibling::div[contains(@class, 'req-details-div-data')]"
                return driver.find_element(By.XPATH, path).text.strip()
            except: return "N/A"
        
        data = {"Address": find_val("Facility Address"), "Shift": find_val("Shift Type"), "Weeks": find_val("Weeks")}
        
        close_btn = driver.find_element(By.CSS_SELECTOR, "button.close.jqmClose")
        driver.execute_script("arguments[0].click();", close_btn)
        # Wait for modal backdrop to vanish
        wait.until(EC.invisibility_of_element_located((By.ID, "viewReqModalContent")))
        return data
    except: return {"Address": "N/A", "Shift": "N/A", "Weeks": "N/A"}

def save_to_db(cur, conn, job_id, details, rates):
    query = """
        INSERT INTO hwl_details (job_id, address, shift, weeks, pay_rates, last_updated)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (job_id) DO UPDATE SET
            address = EXCLUDED.address, shift = EXCLUDED.shift,
            weeks = EXCLUDED.weeks, pay_rates = EXCLUDED.pay_rates,
            last_updated = CURRENT_TIMESTAMP;
    """
    cur.execute(query, (job_id, details["Address"], details["Shift"], details["Weeks"], json.dumps(rates)))
    conn.commit()

try:
    db_conn, db_cur = init_db()
    print("Navigating to Login...")
    driver.get(LOGIN_URL)
    wait.until(EC.element_to_be_clickable((By.ID, "loginName"))).send_keys(USERNAME)
    driver.find_element(By.ID, "loginPasswordField").send_keys(PASSWORD)
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, "input[type='submit'].blue-btn"))
    
    time.sleep(8) 
    driver.get(DATA_URL)
    
    current_page = 1
    while True:
        print(f"\n--- SCRAPING PAGE {current_page} ---")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "locum-requsition-req-padding")))
        time.sleep(3)
        
        # Selector for the Job ID links
        link_css = "ul.locum-requsition-req-padding li a[onclick*='viewRequisition']"
        
        # Determine how many links are on the page
        links = driver.find_elements(By.CSS_SELECTOR, link_css)
        num_links = len(links)

        for i in range(num_links):
            try:
                # Re-locate links to avoid StaleElementReferenceException
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, link_css)))
                current_links = driver.find_elements(By.CSS_SELECTOR, link_css)
                target_link = current_links[i]
                job_id = target_link.text.strip()
                
                # Find the parent row of this specific link
                row = target_link.find_element(By.XPATH, "./ancestor::tr")
                rates_btn = row.find_element(By.XPATH, ".//a[contains(., 'View Rates')]")

                # Step 1: Standard Details
                driver.execute_script("arguments[0].click();", target_link)
                details = scrape_modal_details()
                time.sleep(1) # Stability wait

                # Step 2: Pay Rates
                # Must re-find rates_btn because the DOM might have updated after modal 1
                row = driver.find_elements(By.CSS_SELECTOR, link_css)[i].find_element(By.XPATH, "./ancestor::tr")
                rates_btn = row.find_element(By.XPATH, ".//a[contains(., 'View Rates')]")
                
                driver.execute_script("arguments[0].click();", rates_btn)
                rates = scrape_rates_modal()
                time.sleep(1) # Stability wait

                save_to_db(db_cur, db_conn, job_id, details, rates)
                print(f" [+] Processed {job_id}")

            except Exception as e:
                print(f" [!] Error on item {i}: {e}")
                driver.execute_script("window.scrollTo(0, 0);") # Reset view if lost
                continue

        # Pagination
        try:
            next_btn = driver.find_elements(By.XPATH, f"//a[@class='step' and text()='{current_page + 1}']")
            if next_btn:
                driver.execute_script("arguments[0].click();", next_btn[0])
                current_page += 1
                time.sleep(5)
            else: break
        except: break

except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
finally:
    if 'db_cur' in locals(): db_cur.close()
    if 'db_conn' in locals(): db_conn.close()
    driver.quit()