import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration ---
DB_CONFIG = {
    "dbname": "jobboard",
    "user": "development",
    "password": "PATTERNS@123",
    "host": "localhost",
    "port": "5432"
}

USERNAME = "am@patternshiring.com"
PASSWORD = "Patterns@2026"
LOGIN_URL = "https://westwaysstaffing.securedportals.com/VMS/vms_supplier_login.aspx"
CANDIDATE_URL = "https://westwaysstaffing.securedportals.com/VMS/vms-supplier-candidate-search.aspx"

def get_driver():
    edge_options = Options()
    # edge_options.add_argument("--headless") # Uncomment to run in background
    return webdriver.Edge(options=edge_options)

def save_candidates_to_db(client_id, client_name, candidate_list):
    """Syncs candidates: Adds new, updates existing, deletes missing for this client."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        current_scrape_ids = [can['Appl #'] for can in candidate_list]
        
        for can in candidate_list:
            cur.execute("""
                INSERT INTO westway_candidates (
                    appl_id, company_id, company_name, status, first_name, 
                    last_name, mi, ssn, city, email, home_phone, 
                    cell_phone, date_available, last_updated
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (appl_id) 
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    mi = EXCLUDED.mi,
                    ssn = EXCLUDED.ssn,
                    city = EXCLUDED.city,
                    email = EXCLUDED.email,
                    home_phone = EXCLUDED.home_phone,
                    cell_phone = EXCLUDED.cell_phone,
                    date_available = EXCLUDED.date_available,
                    last_updated = CURRENT_TIMESTAMP;
            """, (
                can['Appl #'], client_id, client_name, can['Status'], can['First Name'],
                can['Last Name'], can['MI'], can['SSN'], can['City'], can['Email'],
                can['Home Phone'], can['Cell Phone'], can['Date Available']
            ))

        # Cleanup: Delete candidates no longer on the portal for THIS client
        if current_scrape_ids:
            cur.execute("""
                DELETE FROM westway_candidates 
                WHERE company_id = %s AND appl_id NOT IN %s
            """, (client_id, tuple(current_scrape_ids)))
        elif not candidate_list:
            # If the scrape returned 0 candidates, delete all records for this client
            cur.execute("DELETE FROM candidates WHERE company_id = %s", (client_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"      [Database] Synced {len(candidate_list)} candidates successfully.")
    except Exception as e:
        print(f"      [Database Error] {e}")

def scrape_page_data(driver):
    """Scrapes the visible table on the current page."""
    page_results = []
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.go")
        for row in rows:
            cells = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            if len(cells) >= 11:
                page_results.append({
                    "Appl #": cells[0], "Status": cells[1], "First Name": cells[2],
                    "Last Name": cells[3], "MI": cells[4], "SSN": cells[5],
                    "City": cells[6], "Email": cells[7], "Home Phone": cells[8],
                    "Cell Phone": cells[9], "Date Available": cells[10]
                })
    except Exception as e:
        print(f"      [!] Error parsing table row: {e}")
    return page_results

def scrape_all_pages(driver, wait):
    """Handles pagination by clicking through all .pager links."""
    all_data = []
    
    # Scrape Page 1
    print("      Scraping Page 1...")
    all_data.extend(scrape_page_data(driver))
    
    try:
        # Check for pagination links
        pagers = driver.find_elements(By.CSS_SELECTOR, ".pagging .pager")
        
        # If there are multiple pages (index 0 is Page 1)
        if len(pagers) > 1:
            # Loop starting from the second page link
            for i in range(1, len(pagers)):
                # Re-find elements to avoid StaleElementReferenceException
                current_pagers = driver.find_elements(By.CSS_SELECTOR, ".pagging .pager")
                target_page = current_pagers[i]
                page_label = target_page.get_attribute("data-page")
                
                print(f"      Navigating to Page (Data-ID: {page_label})...")
                driver.execute_script("arguments[0].click();", target_page)
                
                # Wait for update
                time.sleep(3) 
                wait.until(EC.presence_of_element_located((By.ID, "tbl")))
                
                all_data.extend(scrape_page_data(driver))
    except Exception as e:
        print(f"      [!] Pagination finished or encountered error: {e}")
        
    return all_data

# --- Main Logic ---

# 1. Fetch Client List
initial_driver = get_driver()
initial_wait = WebDriverWait(initial_driver, 20)
client_names = []

try:
    initial_driver.get(LOGIN_URL)
    initial_wait.until(EC.presence_of_element_located((By.ID, "user_name"))).send_keys(USERNAME)
    initial_driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
    initial_driver.find_element(By.ID, "btnLogin").click()

    client_input = initial_wait.until(EC.element_to_be_clickable((By.ID, "tags")))
    client_input.send_keys("a")
    time.sleep(2)
    items = initial_driver.find_elements(By.XPATH, "//ul[contains(@class, 'ui-autocomplete')]//li/a")
    client_names = [i.get_attribute("innerText").strip() for i in items if i.get_attribute("innerText").strip()]
    print(f"Master list: {len(client_names)} clients found.")
finally:
    initial_driver.quit()

# 2. Process each client
for name in client_names:
    print(f"\n===> Processing Client: {name}")
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    
    try:
        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.ID, "user_name"))).send_keys(USERNAME)
        driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
        driver.find_element(By.ID, "btnLogin").click()

        # Select Supplier
        client_input = wait.until(EC.element_to_be_clickable((By.ID, "tags")))
        client_input.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
        search_term = name.split(" - ")[0] if " - " in name else name[:8]
        client_input.send_keys(search_term)
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//a[contains(., '{name}')]"))).click()
        driver.find_element(By.ID, "btnClient").click()
        
        # Navigate to Candidate Search
        time.sleep(2)
        driver.get(CANDIDATE_URL)
        wait.until(EC.presence_of_element_located((By.ID, "tbl")))
        
        # Scrape all pages
        all_candidates = scrape_all_pages(driver, wait)
        
        # Database Sync
        c_id = name.split(" - ")[0] if " - " in name else "Unknown"
        c_name = name.split(" - ")[1] if " - " in name else name
        save_candidates_to_db(c_id, c_name, all_candidates)

    except Exception as e:
        print(f"      [!] Process error for {name}: {e}")
    finally:
        driver.quit()

print("\n--- ALL CLIENTS PROCESSED ---")