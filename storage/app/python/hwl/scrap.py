import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
LOGIN_URL = "https://vms.hwlmsp.com/shiftrock/user/login"
DATA_URL = "https://vms.hwlmsp.com/shiftrock/requisitionLocum/agencyLocumRequisition"
USERNAME = "dhruvil.jaiswal@patternshiring.com"
PASSWORD = "Windows#1"
EXCEL_FILE = "HWL_Requisitions.xlsx"

edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_experimental_option("detach", True) 
driver = webdriver.Edge(options=edge_options)

def human_type(element, text):
    element.click()
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(0.05)

def scrape_hwl_table():
    """
    Refined Scraper: Targets the specific 'requisitionContainer' div structure.
    Extracts the ID from the first <li> anchor and formats the date cleanly.
    """
    js_script = """
    let rows = document.querySelectorAll('table tbody tr');
    let data = [];
    rows.forEach(row => {
        let cells = row.querySelectorAll('td');
        if(cells.length >= 5) {
            
            // 1. EXTRACT JOB ID
            // We target the first <li> within the first <ul> inside the container
            let container = cells[3].querySelector('#requisitionContainer');
            let jobId = "N/A";
            if (container) {
                let firstLink = container.querySelector('ul li a');
                if (firstLink) {
                    jobId = firstLink.innerText.trim();
                }
            }

            // 2. EXTRACT START DATE
            // Targets the .timeBlock and removes extra newlines/spaces
            let startBlock = cells[4].querySelector('.timeBlock');
            let startDate = "N/A";
            if (startBlock) {
                startDate = startBlock.innerText.replace(/\\s+/g, ' ').trim();
            }

            data.push({
                "Dates": startDate,
                "Facility": cells[0].innerText.trim().split('\\n')[0],
                "Job Title": cells[2].innerText.trim(),
                "Job_ID": jobId,
                "Specialty": cells[1].innerText.trim().replace(/\\n/g, " | ")
            });
        }
    });
    return data;
    """
    return driver.execute_script(js_script)

try:
    print("Navigating to HWL Login...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 30)

    # 1. LOGIN
    user_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], input[name='username']")))
    human_type(user_field, USERNAME)
    
    pass_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
    human_type(pass_field, PASSWORD)
    
    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')] | //input[@value='Login']")))
    login_btn.click()

    # 2. NAVIGATE TO REQUISITIONS
    time.sleep(12) 
    driver.get(DATA_URL)
    
    all_raw_data = [] 
    current_page = 1

    # 3. PAGINATION LOOP
    while True:
        print(f"Scraping Page {current_page}...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        # HWL is slow; wait for the 'N/A' placeholders to be replaced by actual data
        time.sleep(10) 
        
        page_data = scrape_hwl_table()
        all_raw_data.extend(page_data) 
        print(f"Added {len(page_data)} rows. Total so far: {len(all_raw_data)}")

        # Check for Next Page
        try:
            next_page_val = str(current_page + 1)
            pagination_xpath = f"//div[contains(@class, 'fr')]//a[@class='step' and text()='{next_page_val}']"
            next_page_btn = driver.find_elements(By.XPATH, pagination_xpath)
            
            if next_page_btn:
                driver.execute_script("arguments[0].click();", next_page_btn[0])
                current_page += 1
            else:
                next_arrow = driver.find_elements(By.XPATH, "//div[contains(@class, 'fr')]//a[contains(text(), '›')]")
                if next_arrow:
                    driver.execute_script("arguments[0].click();", next_arrow[0])
                    current_page += 1
                else:
                    break
        except Exception:
            break

    # 4. SAVE TO EXCEL
    df_new = pd.DataFrame(all_raw_data)
    
    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        # Use Job_ID and Job Title to identify duplicates
        df_final = pd.concat([df_old, df_new]).drop_duplicates(
            subset=['Job_ID', 'Job Title'], 
            keep='first'
        )
    else:
        df_final = df_new

    # Final column arrangement
    cols = ["Dates", "Facility", "Job Title", "Job_ID", "Specialty"]
    df_final = df_final[cols]

    df_final.to_excel(EXCEL_FILE, index=False)
    print("-" * 30)
    print(f"DONE: {len(df_final)} unique jobs saved to {EXCEL_FILE}.")

except Exception as e:
    print(f"Error occurred: {e}")
finally:
    driver.quit()
