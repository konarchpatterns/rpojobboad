import time
import re
import urllib.parse
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# --- CONFIG ---
PORTAL_URL = "https://saintfrancis.vndly.com/sign_in"
CANDIDATES_URL = "https://saintfrancis.vndly.com/candidates?ordering=-created_at&page=1"
USERNAME = "joyson.bejoy@patternshiring.com"
PASSWORD = "Patterns@123"

# --- DATABASE CONFIG ---
DB_USER = "development"
DB_PASS = "PATTERNS@123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "jobboard"

encoded_pass = urllib.parse.quote_plus(DB_PASS)
engine = create_engine(f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 30)

def init_db():
    """Ensures the candidates table exists with the correct primary key."""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rsprimary_candidates (
                unique_id TEXT PRIMARY KEY,
                name TEXT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                vendor TEXT,
                experience TEXT,
                bill_rate TEXT,
                ssn_last_4 TEXT,
                skills TEXT,
                profile_url TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

def upsert_candidate(data):
    """Inserts new data or updates existing rows based on unique_id."""
    with engine.begin() as conn:
        upsert_query = text("""
            INSERT INTO rsprimary_candidates (
                unique_id, name, first_name, last_name, email, phone, 
                address, vendor, experience, bill_rate, ssn_last_4, skills, profile_url
            ) VALUES (
                :unique_id, :name, :first_name, :last_name, :email, :phone, 
                :address, :vendor, :experience, :bill_rate, :ssn_last_4, :skills, :profile_url
            )
            ON CONFLICT (unique_id) DO UPDATE SET
                name = EXCLUDED.name,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                address = EXCLUDED.address,
                vendor = EXCLUDED.vendor,
                experience = EXCLUDED.experience,
                bill_rate = EXCLUDED.bill_rate,
                ssn_last_4 = EXCLUDED.ssn_last_4,
                skills = EXCLUDED.skills,
                profile_url = EXCLUDED.profile_url,
                last_updated = CURRENT_TIMESTAMP;
        """)
        conn.execute(upsert_query, data)

def delete_stale_candidates(seen_ids):
    """Removes candidates from the DB that were not found during this scrape."""
    if not seen_ids:
        return
    with engine.begin() as conn:
        # Delete rows where unique_id is not in the list of currently visible IDs
        query = text("DELETE FROM rsprimary_candidates WHERE unique_id NOT IN :seen_ids")
        result = conn.execute(query, {"seen_ids": tuple(seen_ids)})
        print(f"Cleanup: Removed {result.rowcount} candidates no longer on the portal.")

def get_candidate_links():
    js_extract = """
    let results = [];
    let items = document.querySelectorAll('[data-testid="items-list-item"]');
    items.forEach(item => {
        let nameEl = item.querySelector('[data-testid="candidate_name"]');
        let linkEl = item.querySelector('a[data-title-lockup-heading-link="true"]');
        let uniqueIdEl = item.querySelector('[data-testid="candidate_unique_id"]');
        if (linkEl && nameEl) {
            results.push({
                "name": nameEl.innerText.trim(),
                "url": linkEl.href,
                "unique_id": uniqueIdEl ? uniqueIdEl.innerText.replace('Candidate Unique ID', '').trim() : ""
            });
        }
    });
    return results;
    """
    return driver.execute_script(js_extract)

def scrape_candidate_details(url):
    driver.get(url)
    try:
        wait.until(EC.presence_of_element_located((By.ID, "general")))
    except: return None

    js_details = """
    let data = {};
    const getVal = (id) => {
        let el = document.querySelector(`[data-testid="${id}"] p:nth-child(2)`);
        return el ? el.innerText.trim() : "";
    };
    data["first_name"] = getVal("candidate_first_name");
    data["last_name"] = getVal("candidate_last_name");
    data["email"] = getVal("email");
    data["phone"] = getVal("contact_number");
    data["address"] = getVal("address_line_one");
    data["vendor"] = getVal("vendor_entity");
    data["experience"] = getVal("experience");
    data["bill_rate"] = getVal("candidate_bill_rate_hourly");
    data["ssn_last_4"] = document.querySelector('[aria-label="SSN Last 4 Digits"]')?.innerText || "";
    let skills = [];
    document.querySelectorAll('[data-testid="candidate_skills"]').forEach(s => skills.push(s.innerText.trim()));
    data["skills"] = skills.join(", ");
    return data;
    """
    return driver.execute_script(js_details)

try:
    init_db()
    print("Logging in...")
    driver.get(PORTAL_URL)

    # Login sequence
    user_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input")))
    ActionChains(driver).move_to_element(user_field).click().send_keys(USERNAME).perform()
    driver.find_element(By.XPATH, "//button[contains(., 'Continue')]").click()

    pass_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
    ActionChains(driver).move_to_element(pass_field).click().send_keys(PASSWORD).perform()
    driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Sign In')]").click()

    time.sleep(8)
    driver.get(CANDIDATES_URL)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="items-list-item"]')))
    
    candidate_list = get_candidate_links()
    print(f"Found {len(candidate_list)} candidates on the portal. Starting sync...")

    scraped_ids = []

    for candidate in candidate_list:
        print(f"Processing: {candidate['name']} ({candidate['unique_id']})...")
        details = scrape_candidate_details(candidate['url'])
        
        if details:
            db_data = {
                "unique_id": candidate['unique_id'],
                "name": candidate['name'],
                "profile_url": candidate['url'],
                **details
            }
            # Add to list of seen IDs for final cleanup
            scraped_ids.append(candidate['unique_id'])
            # Save or Update immediately
            upsert_candidate(db_data)
        
        time.sleep(1)

    # Final cleanup: Remove anyone in DB who wasn't seen in this scrape
    delete_stale_candidates(scraped_ids)

    print("Sync process completed successfully.")

except Exception as e:
    print(f"Global Error: {e}")
finally:
    driver.quit()