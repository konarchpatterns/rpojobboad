import time
import pandas as pd
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
# Database Setup
db_user = "development"
db_pass = quote_plus("PATTERNS@123") 
db_host = "localhost"
db_port = "5432"
db_name = "jobboard"
DB_URL = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# URLs & Credentials
LOGIN_URL = "https://vms.hwlmsp.com/shiftrock/user/login"
STAFF_POOL_URL = "https://vms.hwlmsp.com/shiftrock/agencyProfile/loadRnsList"
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Windows#1"

# --- SELENIUM SETUP ---
edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_argument("--disable-blink-features=AutomationControlled")
edge_options.add_argument("--ignore-certificate-errors")
edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Edge(options=edge_options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
wait = WebDriverWait(driver, 30)

def extract_candidate_data(profile_id):
    """Extracts all personal info and includes the profile_id as the primary key."""
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "label")))
        def get_val(label_name):
            try:
                xpath = f"//span[contains(@class, 'label') and contains(normalize-space(), '{label_name}')]/following-sibling::span[contains(@class, 'labelTxt')][1]"
                return driver.find_element(By.XPATH, xpath).text.strip()
            except: return "N/A"

        return {
            "profile_id": profile_id,
            "first_name": get_val("First Name"),
            "middle_name": get_val("Middle Name"),
            "last_name": get_val("Last Name"),
            "dob": get_val("Date of Birth"),
            "gender": get_val("Gender"),
            "email": get_val("Email"),
            "mobile": get_val("Mobile Number"),
            "address_1": get_val("Address Line 1"),
            "city": get_val("City"),
            "state": get_val("State"),
            "zip_code": get_val("Zip Code"),
            "dist_pref": get_val("Preferred Distance to Work")
        }
    except: return None

try:
    # 1. DATABASE INITIALIZATION
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hwl_candidates (
                profile_id VARCHAR(50) PRIMARY KEY,
                first_name TEXT, middle_name TEXT, last_name TEXT,
                dob TEXT, gender TEXT, email TEXT, mobile TEXT,
                address_1 TEXT, city TEXT, state TEXT, zip_code TEXT,
                dist_pref TEXT, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

    # 2. LOGIN
    print("Logging in...")
    driver.get(LOGIN_URL)
    wait.until(EC.element_to_be_clickable((By.ID, "loginName"))).send_keys(USERNAME)
    driver.find_element(By.ID, "loginPasswordField").send_keys(PASSWORD)
    login_btn = driver.find_element(By.CSS_SELECTOR, "input.btn.blue-btn[value='Login']")
    driver.execute_script("arguments[0].click();", login_btn)

    time.sleep(8)
    driver.get(STAFF_POOL_URL)
    main_window = driver.current_window_handle
    
    all_scraped_data = []
    page_num = 1

    # 3. SCRAPING LOOP
    while True:
        print(f"\n--- SCRAPING PAGE {page_num} ---")
        wait.until(EC.presence_of_element_located((By.ID, "nurseTable")))
        links = driver.find_elements(By.CSS_SELECTOR, "a.contract-profile")

        for i in range(len(links)):
            current_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.contract-profile")))
            link = current_links[i]
            
            # Extract Profile ID from onclick attribute: openFacilitySpecific(208822, 99325)
            onclick_val = link.get_attribute("onclick")
            profile_id = onclick_val.split('(')[1].split(',')[0].strip()

            driver.execute_script("arguments[0].click();", link)
            entire_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Entire Profile')]")))
            driver.execute_script("arguments[0].click();", entire_btn)
            
            time.sleep(5)
            
            handles = driver.window_handles
            if len(handles) > 1:
                driver.switch_to.window(handles[-1])
                data = extract_candidate_data(profile_id)
                if data:
                    all_scraped_data.append(data)
                    print(f" [+] Scraped: {data['first_name']} {data['last_name']}")
                driver.close()
                driver.switch_to.window(main_window)
            else:
                data = extract_candidate_data(profile_id)
                if data: all_scraped_data.append(data)
                driver.get(STAFF_POOL_URL)
                wait.until(EC.presence_of_element_located((By.ID, "nurseTable")))

        # Pagination logic
        next_btns = driver.find_elements(By.CSS_SELECTOR, "a.nextLink")
        if next_btns:
            driver.execute_script("arguments[0].click();", next_btns[0])
            page_num += 1
            time.sleep(5)
        else:
            break

    # 4. DATABASE SYNC (UPSERT & CLEANUP)
    if all_scraped_data:
        print(f"\nSyncing {len(all_scraped_data)} records to PostgreSQL...")
        df = pd.DataFrame(all_scraped_data)
        df.to_sql('candidates_temp', engine, if_exists='replace', index=False)

        with engine.begin() as conn:
            # 1. Update/Insert records from temp table
            conn.execute(text("""
                INSERT INTO hwl_candidates (
                    profile_id, first_name, middle_name, last_name, dob, gender, 
                    email, mobile, address_1, city, state, zip_code, dist_pref, last_updated
                )
                SELECT 
                    profile_id, first_name, middle_name, last_name, dob, gender, 
                    email, mobile, address_1, city, state, zip_code, dist_pref, CURRENT_TIMESTAMP 
                FROM candidates_temp
                ON CONFLICT (profile_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    middle_name = EXCLUDED.middle_name,
                    last_name = EXCLUDED.last_name,
                    dob = EXCLUDED.dob,
                    gender = EXCLUDED.gender,
                    email = EXCLUDED.email,
                    mobile = EXCLUDED.mobile,
                    address_1 = EXCLUDED.address_1,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state,
                    zip_code = EXCLUDED.zip_code,
                    dist_pref = EXCLUDED.dist_pref,
                    last_updated = CURRENT_TIMESTAMP;
            """))

            # 2. Delete records NOT in the current scrape (Sync removal)
            conn.execute(text("DELETE FROM hwl_candidates WHERE profile_id NOT IN (SELECT profile_id FROM candidates_temp)"))
            conn.execute(text("DROP TABLE candidates_temp"))
            
        print("Database sync complete.")

except Exception as e:
    print(f"Fatal Error: {e}")
finally:
    driver.quit()