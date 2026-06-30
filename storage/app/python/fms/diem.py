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
db_user = "development"
db_pass = quote_plus("PATTERNS@123") 
db_host = "localhost"
db_port = "5432"
db_name = "jobboard"
DB_URL = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

LOGIN_URL = "https://fms.favoritestaffing.com/index.html#!/login"
USERNAME = "SJosePatterns"
PASSWORD = "Monsoon@2022"

edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 35)

try:
    # 1. DATABASE INITIALIZATION
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS favorite_staffing (
                order_id VARCHAR(50) PRIMARY KEY,
                order_type TEXT,
                status TEXT,
                location TEXT,
                start_date TEXT,
                end_date TEXT,
                shift TEXT,
                hours TEXT,
                job_class TEXT,
                area TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
    
    # 2. LOGIN PROCESS
    print("Navigating to Login...")
    driver.get(LOGIN_URL)
    vendor_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.recruiter")))
    vendor_link.click()
    
    wait.until(EC.presence_of_element_located((By.ID, "userNameValue")))
    driver.find_element(By.ID, "userNameValue").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    
    login_btn = driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
    driver.execute_script("arguments[0].click();", login_btn)

    # 3. NAVIGATION (CLICK VIEW ALL)
    print("Waiting for Dashboard...")
    time.sleep(12)
    view_all_xpath = "//span[contains(text(), 'Open Per diem Orders')]/ancestor::article//button[contains(., 'View All')]"
    view_all_btn = wait.until(EC.element_to_be_clickable((By.XPATH, view_all_xpath)))
    driver.execute_script("arguments[0].click();", view_all_btn)
    print("Clicked View All.")

    # 4. SCRAPING THE ORDERS TABLE
    print("Waiting for orders search table...")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-browser-view")))
    time.sleep(5) 

    scraped_data = []
    current_page = 1

    while True:
        print(f"Scraping Page {current_page}...")
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.table-browser-view")
        
        for row in rows:
            # We use a helper function to find spans by their preceding label text
            def get_val(label_text):
                try:
                    # XPath finds the label with specific text and gets the following span
                    xpath = f".//label[contains(text(), '{label_text}')]/following-sibling::span"
                    return row.find_element(By.XPATH, xpath).text.strip()
                except:
                    return "N/A"

            scraped_data.append({
                "order_id": get_val("Order ID:"),
                "order_type": get_val("Order Type:"),
                "status": get_val("Status:"),
                "location": get_val("Location:"),
                "start_date": get_val("Start Date:"),
                "end_date": get_val("End Date:"),
                "shift": get_val("Shift:"),
                "hours": get_val("Hours:"),
                "job_class": get_val("Class:"),
                "area": get_val("Area:")
            })

        print(f"Found {len(rows)} items on this page.")

        # Pagination Logic based on your provided <nav> HTML
        try:
            # Check the 'Next' li element. If it has class 'disabled', we stop.
            next_li = driver.find_element(By.XPATH, "//li[contains(@class, 'next')]")
            if "disabled" in next_li.get_attribute("class"):
                print("No more pages (Next button disabled).")
                break
            else:
                next_link = next_li.find_element(By.TAG_NAME, "span") # In your HTML, clickable part is a span
                driver.execute_script("arguments[0].click();", next_link)
                current_page += 1
                time.sleep(6)
        except Exception:
            break

    # 5. POSTGRES SYNC
    if scraped_data:
        print(f"Syncing {len(scraped_data)} records...")
        df = pd.DataFrame(scraped_data).drop_duplicates(subset=['order_id'])
        # Rename job_class to match SQL if necessary
        df.to_sql('fs_staging', engine, if_exists='replace', index=False)

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO favorite_staffing (order_id, order_type, status, location, start_date, end_date, shift, hours, job_class, area)
                SELECT order_id, order_type, status, location, start_date, end_date, shift, hours, job_class, area FROM fs_staging
                ON CONFLICT (order_id) DO UPDATE SET
                    order_type = EXCLUDED.order_type,
                    status = EXCLUDED.status,
                    location = EXCLUDED.location,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    shift = EXCLUDED.shift,
                    hours = EXCLUDED.hours,
                    job_class = EXCLUDED.job_class,
                    area = EXCLUDED.area,
                    last_seen = CURRENT_TIMESTAMP;
                
                DELETE FROM favorite_staffing WHERE order_type = 'Per Diem' and order_id NOT IN (SELECT order_id FROM fs_staging);
                DROP TABLE fs_staging;
            """))
        print("Success: Database is synchronized.")
    else:
        print("No data captured.")

except Exception as e:
    print(f"Fatal Error: {e}")
finally:
    driver.quit()
