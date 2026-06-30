import time
import pandas as pd
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, text
from selenium.common.exceptions import TimeoutException

# --- CONFIGURATION ---
db_user = "development"
db_pass = quote_plus("PATTERNS@123") 
db_host = "localhost"
db_port = "5432"
db_name = "jobboard"
DB_URL = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

LOGIN_URL = "https://vms.laboredge.com/signin"
CANDIDATE_URL = "https://vms.laboredge.com/supplier/candidates"

USERNAME = "pooja.raut@patternshiring.com"
PASSWORD = "Patterns@123"
ORG_CODE = "NS"

def get_driver():
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    # edge_options.add_argument("--headless") # Uncomment to run in background
    return webdriver.Edge(options=edge_options)

def get_clean_text(cell):
    """Extracts text from LaborEdge ellipsis spans or titles."""
    try:
        span = cell.find_element(By.TAG_NAME, "span")
        title = span.get_attribute("title")
        return title.strip() if title else span.text.strip()
    except:
        return cell.text.strip()

def main():
    driver = get_driver()
    wait = WebDriverWait(driver, 35)
    engine = create_engine(DB_URL)
    
    scraped_data = []

    try:
        # 1. LOGIN
        print("Logging into LaborEdge...")
        driver.get(LOGIN_URL)
        wait.until(EC.element_to_be_clickable((By.ID, "email"))).send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.ID, "organizationCode").send_keys(ORG_CODE)
        
        login_btn = driver.find_element(By.XPATH, "//span[text()='LOGIN']/ancestor::button")
        driver.execute_script("arguments[0].click();", login_btn)

        # 2. SESSION MODAL HANDLING
        print("Checking for session confirmation modal...")
        try:
            # Targeted XPath for your specific DOM structure
            yes_button_xpath = "//div[contains(@class, 'popup-container')]//span[text()='Yes']/ancestor::button"
            
            # Wait up to 5 seconds for the modal to appear
            yes_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, yes_button_xpath))
            )
            print("Confirmation modal detected. Clicking 'Yes'...")
            driver.execute_script("arguments[0].click();", yes_btn)
            time.sleep(2) 
        except TimeoutException:
            print("No confirmation modal appeared. Proceeding...")

        # 3. NAVIGATION TO CANDIDATES
        print("Navigating to Candidates page...")
        time.sleep(10) # Wait for post-login dashboard load
        driver.get(CANDIDATE_URL)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-datatable-tbody")))
        time.sleep(5) 

        # 4. SCRAPING WITH PAGINATION
        current_page = 1
        while True:
            print(f"Scraping Page {current_page}...")
            rows = driver.find_elements(By.CSS_SELECTOR, ".p-datatable-tbody tr")
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 7:
                    scraped_data.append({
                        "name": get_clean_text(cells[0]),
                        "email": get_clean_text(cells[1]),
                        "phone": get_clean_text(cells[2]),
                        "state": get_clean_text(cells[3]),
                        "status": get_clean_text(cells[4]),
                        "profession": get_clean_text(cells[5]),
                        "specialty": get_clean_text(cells[6])
                    })

            # Check for Next Page (Pagination)
            try:
                next_btn_icon = driver.find_element(By.CLASS_NAME, "pi-angle-right")
                next_btn = next_btn_icon.find_element(By.XPATH, "./ancestor::button")
                
                # Check if button is active and not disabled
                if next_btn.is_enabled() and "disabled" not in next_btn.get_attribute("class"):
                    print("Moving to next page...")
                    driver.execute_script("arguments[0].click();", next_btn)
                    current_page += 1
                    time.sleep(6) # Angular refresh wait
                else:
                    print("Reached final page.")
                    break
            except:
                print("No pagination button found.")
                break

        # 5. POSTGRES SYNCHRONIZATION (Truncate and Insert)
        if scraped_data:
            print(f"Captured {len(scraped_data)} total records. Syncing with database...")
            
            # Remove internal duplicates from the scrape results
            df = pd.DataFrame(scraped_data).drop_duplicates(subset=['email'])

            with engine.begin() as conn:
                # Step A: Clear the table (handles removals from the portal)
                conn.execute(text("TRUNCATE TABLE vms_candidates;"))
                
                # Step B: Insert all currently visible portal data
                df.to_sql('vms_candidates', conn, if_exists='append', index=False)
            
            print("Successfully synced: Database matches current portal data.")
        else:
            print("No data captured. Check selectors or table visibility.")

    except Exception as e:
        print(f"Fatal Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()