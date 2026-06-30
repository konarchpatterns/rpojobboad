import time
import pandas as pd
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, text
from selenium.common.exceptions import NoSuchElementException

# --- CONFIGURATION ---
db_user = "development"
db_pass = quote_plus("PATTERNS@123") 
db_host = "localhost"
db_port = "5432"
db_name = "jobboard"
DB_URL = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

LOGIN_URL = "https://fms.favoritestaffing.com/index.html#!/login"
EMPLOYEES_URL = "https://fms.favoritestaffing.com/index.html#!/employees"
USERNAME = "SJosePatterns"
PASSWORD = "Monsoon@2022"

def get_driver():
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    return webdriver.Edge(options=edge_options)

def get_val(row, label_text):
    try:
        xpath = f".//label[contains(text(), '{label_text}')]/following-sibling::span"
        return row.find_element(By.XPATH, xpath).text.strip()
    except NoSuchElementException:
        return "N/A"

def main():
    driver = get_driver()
    wait = WebDriverWait(driver, 35)
    engine = create_engine(DB_URL)
    
    scraped_data = []

    try:
        # 1. LOGIN
        print("Logging into Favorite Staffing...")
        driver.get(LOGIN_URL)
        vendor_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.recruiter")))
        vendor_link.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "userNameValue")))
        driver.find_element(By.ID, "userNameValue").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        
        login_btn = driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
        driver.execute_script("arguments[0].click();", login_btn)

        # 2. NAVIGATION
        time.sleep(10)
        print(f"Navigating to: {EMPLOYEES_URL}")
        driver.get(EMPLOYEES_URL)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-condensed")))

        # 3. SCRAPING
        current_page = 1
        while True:
            print(f"Scraping Page {current_page}...")
            time.sleep(3) 
            rows = driver.find_elements(By.CSS_SELECTOR, "tr.table-browser-view")
            
            for row in rows:
                scraped_data.append({
                    "last_name": get_val(row, "Last Name:"),
                    "first_name": get_val(row, "First Name:"),
                    "job_class": get_val(row, "Class:"),
                    "area": get_val(row, "Area:"),
                    "status": get_val(row, "Scheduling Status:"),
                    "last_worked": get_val(row, "Last Worked Date:")
                })

            # Pagination
            try:
                next_li = driver.find_element(By.XPATH, "//li[contains(@class, 'next')]")
                if "disabled" in next_li.get_attribute("class"):
                    break
                else:
                    next_btn = next_li.find_element(By.TAG_NAME, "a")
                    driver.execute_script("arguments[0].click();", next_btn)
                    current_page += 1
                    time.sleep(5)
            except:
                break

        # 4. DATABASE SYNC (UPSERT & DELETE)
        if scraped_data:
            print(f"Captured {len(scraped_data)} candidates. Syncing...")
            df = pd.DataFrame(scraped_data)
            # Create a combined staging table
            df.to_sql('fms_staging', engine, if_exists='replace', index=False)

            with engine.begin() as conn:
                # A. Update/Insert: Using first_name and last_name as the composite key
                conn.execute(text("""
                    -- Note: This approach handles cases where you don't have a unique ID column
                    -- We delete matching names from the main table first, then insert everything from staging
                    -- This effectively acts as an 'Update'
                    DELETE FROM fms_candidates 
                    WHERE (first_name, last_name) IN (SELECT first_name, last_name FROM fms_staging);

                    INSERT INTO fms_candidates (first_name, last_name, job_class, area, status, last_worked, last_seen)
                    SELECT first_name, last_name, job_class, area, status, last_worked, CURRENT_TIMESTAMP FROM fms_staging;
                    
                    -- B. Remove: Delete from main table if NOT in the current scrape
                    DELETE FROM fms_candidates 
                    WHERE (first_name, last_name) NOT IN (SELECT first_name, last_name FROM fms_staging);
                    
                    DROP TABLE fms_staging;
                """))
            print("Successfully synced: Added new, updated existing, and removed old candidates.")
        else:
            print("No data found to sync.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()