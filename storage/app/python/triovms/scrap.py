import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
LOGIN_URL = "https://trio.triovms.com/Agency/LocumsDashboard"
DATA_URL = "https://trio.triovms.com/LocumOrder/Index/Open"
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Recruit@123"
EXCEL_FILE = "TrioVMS_Jobs.xlsx"

edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_argument("--ignore-certificate-errors")
edge_options.add_argument("--ignore-ssl-errors")
driver = webdriver.Edge(options=edge_options)

def scrape_visible_rows():
    """Targeting the DXDataRow structure from the provided grid HTML."""
    js_script = """
    let rows = document.querySelectorAll('tr[id*="DXDataRow"]');
    let data = [];
    rows.forEach(row => {
        let cells = row.querySelectorAll('td.dxgv');
        if(cells.length >= 8) {
            let jobId = cells[2].innerText.trim();
            if(jobId && jobId !== "") {
                data.push({
                    "Status": cells[0].innerText.trim(),
                    "Reason": cells[1].innerText.trim(),
                    "Job Id": jobId,
                    "Type": cells[3].innerText.trim(),
                    "Profession": cells[4].innerText.trim(),
                    "Specialty": cells[5].innerText.trim(),
                    "Facility": cells[6].innerText.trim(),
                    "City": cells[7].innerText.trim(),
                    "State": cells[8].innerText.trim(),
                    "Start": cells[9] ? cells[9].innerText.trim() : "",
                    "Bid Due Date": cells[11] ? cells[11].innerText.trim() : ""
                });
            }
        }
    });
    return data;
    """
    return driver.execute_script(js_script)

try:
    print("Navigating to TrioVMS SSO...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 45)

    # 1. LOGIN
    user_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
    user_field.send_keys(USERNAME)
    pass_field = driver.find_element(By.ID, "password")
    pass_field.send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # 2. NAVIGATE TO GRID
    time.sleep(15) 
    print("Opening Locums Job Orders...")
    driver.get(DATA_URL)
    
    # 3. INCREMENTAL CONTAINER SCROLL
    all_jobs = {} 
    target_total = 297 # Based on your header
    
    print(f"Targeting {target_total} records. Starting container-level scroll...")
    
    # The container that holds the scrollbar for the table rows
    container_selector = "div.dxgvCSD"
    
    # Wait for the first set of data to appear
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr[id*="DXDataRow"]')))

    attempts_without_new_data = 0
    while len(all_jobs) < target_total and attempts_without_new_data < 20:
        current_batch = scrape_visible_rows()
        
        initial_count = len(all_jobs)
        for job in current_batch:
            all_jobs[job["Job Id"]] = job
        
        new_count = len(all_jobs)
        print(f"Progress: {new_count}/{target_total}")

        if new_count == initial_count:
            attempts_without_new_data += 1
        else:
            attempts_without_new_data = 0

        # Scroll the internal table container by a small amount
        # This triggers the AJAX lazy-load for DevExpress
        driver.execute_script(f"""
            let container = document.querySelector('{container_selector}');
            if(container) {{
                container.scrollTop += 350;
            }}
        """)
        time.sleep(2) # Buffer for virtual row swapping

    # 4. SYNC & SAVE
    if all_jobs:
        df_final = pd.DataFrame(list(all_jobs.values()))
        df_final.to_excel(EXCEL_FILE, index=False)
        print(f"Success! {len(df_final)} unique jobs saved to {EXCEL_FILE}.")
    else:
        print("No data collected.")

except Exception as e:
    print(f"Global Error: {e}")
finally:
    driver.quit()
