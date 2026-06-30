import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. CONFIGURATION ---
DB_CONFIG = {
    "dbname": "jobboard",
    "user": "development",
    "password": "PATTERNS@123",
    "host": "localhost",
    "port": "5432"
}

LOGIN_URL = "https://trio.triovms.com/Agency/LocumsDashboard"
CANDIDATES_URL = "https://trio.triovms.com/Agency/Candidates"
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Recruit@123"

# --- 2. DATABASE LOGIC ---
def upsert_single_candidate(data):
    """Inserts or updates one candidate at a time."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO trovms_candidates (
                candidate_number, candidate_uuid, name, npi, phone, email, 
                years_exp, travel_exp, selling_points, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (candidate_number) 
            DO UPDATE SET 
                candidate_uuid = EXCLUDED.candidate_uuid,
                name = EXCLUDED.name,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                selling_points = EXCLUDED.selling_points,
                last_updated = CURRENT_TIMESTAMP;
        """, (
            data.get('Number'),
            data.get('ID'),
            data.get('Name'),
            data.get('NPI (Provider Id)'),
            data.get('Phone'),
            data.get('Email Address'),
            data.get('Years Experience'),
            data.get('Years Traveling'),
            data.get('Selling Points')
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"   [!] Database Error for {data.get('Name')}: {e}")

def cleanup_stale_candidates(seen_numbers):
    """Removes candidates from DB that were not found in this scrape session."""
    if not seen_numbers:
        return
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM trovms_candidates WHERE candidate_number NOT IN %s", (tuple(seen_numbers),))
        conn.commit()
        print(f"Cleanup complete. Stale records removed.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"   [!] Cleanup Error: {e}")

# --- 3. SCRAPING LOGIC ---
edge_options = Options()
edge_options.add_argument("--start-maximized")
driver = webdriver.Edge(options=edge_options)

def get_visible_candidate_links():
    js_script = """
    let rows = document.querySelectorAll('tr[id*="AgencyCandidateGrid_DXDataRow"]');
    let links = [];
    rows.forEach(row => {
        let nameCell = row.querySelector('td[id*="tccell"] a');
        if(nameCell) {
            links.push({
                "name": nameCell.innerText.trim(),
                "url": nameCell.getAttribute('href')
            });
        }
    });
    return links;
    """
    return driver.execute_script(js_script)

def scrape_detail_page(candidate_url, candidate_name):
    driver.get(f"https://trio.triovms.com{candidate_url}")
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "panel-title")))
    except: return None

    details_script = """
    let result = {};
    let rows = document.querySelectorAll('table.table tr');
    rows.forEach(r => {
        let label = r.querySelector('td.text-semibold')?.innerText.replace(':', '').trim() || "";
        let val = r.querySelector('td.text-right')?.innerText.trim() || "";
        if(label) result[label] = val;
    });
    let sp = document.querySelector('div.ml-15');
    result["Selling Points"] = sp ? sp.innerText.trim() : "";
    let expItems = document.querySelectorAll('ul.list-square li span');
    if(expItems.length >= 2) {
        result["Years Experience"] = expItems[0].innerText;
        result["Years Traveling"] = expItems[1].innerText;
    }
    return result;
    """
    scraped = driver.execute_script(details_script)
    scraped['Name'] = candidate_name
    scraped['ID'] = candidate_url.split('/')[-1]
    return scraped

try:
    print("Logging into TrioVMS...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 30)

    wait.until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    time.sleep(5)
    driver.get(CANDIDATES_URL)
    
    all_candidate_links = {} 
    target_total = 897 
    container_selector = "div.dxgvCSD"

    print("Phase 1: Collecting all candidate URLs...")
    attempts = 0
    while len(all_candidate_links) < target_total and attempts < 15:
        batch = get_visible_candidate_links()
        start_count = len(all_candidate_links)
        for item in batch:
            all_candidate_links[item['url']] = item['name']
        
        if len(all_candidate_links) == start_count: attempts += 1
        else: attempts = 0
        
        driver.execute_script(f"document.querySelector('{container_selector}').scrollTop += 600;")
        time.sleep(1.5)

    print(f"Phase 2: Processing {len(all_candidate_links)} candidates...")
    seen_numbers = []
    
    for url, name in all_candidate_links.items():
        print(f" -> Reading & Saving: {name}")
        profile = scrape_detail_page(url, name)
        
        if profile and profile.get('Number'):
            # SAVE TO DATABASE IMMEDIATELY
            upsert_single_candidate(profile)
            seen_numbers.append(profile['Number'])
            
        time.sleep(0.3) # Small delay to be polite to the server

    # --- FINAL CLEANUP ---
    print("Performing final cleanup of stale records...")
    cleanup_stale_candidates(seen_numbers)

except Exception as e:
    print(f"Global Error: {e}")
finally:
    driver.quit()