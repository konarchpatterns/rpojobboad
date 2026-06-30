import time
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
LOGIN_URL = "https://vms.medefis5.com/"
CANDIDATES_URL = "https://vms.medefis5.com/candidate"
USERNAME = "patterns"
PASSWORD = "PHC!#2026$"

# Database Configuration
DB_USER = "development"
DB_PASS = urllib.parse.quote_plus("PATTERNS@123")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "jobboard"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 30)

def scrape_candidate_table():
    """Extracts candidate data from the ReactTable DOM structure provided."""
    js_script = """
    let rows = document.querySelectorAll('.rt-tr-group');
    let data = [];
    rows.forEach(row => {
        // Find elements by their data-testid within the row
        let nameEl = row.querySelector('[data-testid="candidate-name"] a');
        let emailEl = row.querySelector('[data-testid="candidate-search-email-id"]');
        let stateEl = row.querySelector('[data-testid="candidate-state"] .responsive-value');
        let specEl = row.querySelector('[data-testid="candidate-specialty"] .responsive-value');
        let subSpecEl = row.querySelector('[data-testid="sub-specialty"] .responsive-value');
        
        if (nameEl) {
            data.push({
                "candidate_name": nameEl.innerText.trim(),
                "profile_url": nameEl.getAttribute('href'),
                "candidate_id": nameEl.getAttribute('href').split('/').pop(),
                "email": emailEl ? emailEl.innerText.trim() : "N/A",
                "state": stateEl ? stateEl.innerText.trim() : "N/A",
                "specialty": specEl ? specEl.innerText.trim() : "N/A",
                "sub_specialty": subSpecEl ? subSpecEl.innerText.trim() : "N/A"
            });
        }
    });
    return data;
    """
    return driver.execute_script(js_script)

try:
    print("Navigating to Login...")
    driver.get(LOGIN_URL)
    time.sleep(5)

    # 1. LOGIN
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes: driver.switch_to.frame(0)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text']"))).send_keys(USERNAME)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(., 'Login')]").click()
    driver.switch_to.default_content()

    # 2. NAVIGATE TO CANDIDATES
    time.sleep(10)
    driver.get(CANDIDATES_URL)
    
    all_candidates = []
    current_page = 1

    # 3. PAGINATION LOOP
    while True:
        print(f"Scraping Page {current_page}...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rt-tbody")))
        time.sleep(5) # Allow React to hydrate the rows
        
        page_data = scrape_candidate_table()
        if page_data:
            all_candidates.extend(page_data)
        else:
            break

        # Check for Next Button
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".-next button")
            if "disabled" in next_btn.get_attribute("class") or next_btn.get_property("disabled"):
                break
            driver.execute_script("arguments[0].click();", next_btn)
            current_page += 1
            time.sleep(5)
        except:
            break

    # 4. OUTPUT AND DATABASE SYNC
    if all_candidates:
        df = pd.DataFrame(all_candidates).drop_duplicates(subset=['candidate_id'])
        print("\n--- Scraped Candidates ---")
        print(df[['candidate_name', 'candidate_id', 'email']].head())

        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS medefis_candidates (
                    candidate_name TEXT,
                    candidate_id TEXT PRIMARY KEY,
                    profile_url TEXT,
                    email TEXT,
                    state TEXT,
                    specialty TEXT,
                    sub_specialty TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            df.to_sql("temp_candidates_sync", conn, if_exists="replace", index=False)

            upsert_query = text("""
                INSERT INTO medefis_candidates (candidate_name, candidate_id, profile_url, email, state, specialty, sub_specialty)
                SELECT candidate_name, candidate_id, profile_url, email, state, specialty, sub_specialty FROM temp_candidates_sync
                ON CONFLICT (candidate_id) DO UPDATE SET
                    candidate_name = EXCLUDED.candidate_name,
                    email = EXCLUDED.email,
                    state = EXCLUDED.state,
                    specialty = EXCLUDED.specialty,
                    sub_specialty = EXCLUDED.sub_specialty,
                    last_updated = CURRENT_TIMESTAMP;
            """)
            conn.execute(upsert_query)
            conn.execute(text("DROP TABLE temp_candidates_sync;"))

        print(f"\nSync Complete: {len(df)} candidates processed.")
    else:
        print("No candidates found.")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()