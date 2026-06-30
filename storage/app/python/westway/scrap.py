import time
import pandas as pd
import os
import re
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
PORTAL_URL = "https://westwaysstaffing.securedportals.com/VMS/vms_supplier_login.aspx"
JOBS_URL = "https://westwaysstaffing.securedportals.com/VMS/vms-supplier-open-joborders.aspx"
USERNAME = "am@patternshiring.com"
PASSWORD = "Patterns@2026"

def get_valid_filename(name):
    """Sanitizes the client name for Windows filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_") + ".xlsx"

edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_experimental_option("detach", True) 
driver = webdriver.Edge(options=edge_options)

def get_dynamic_client_list():
    """Stage 1: Discover all client names currently in the system."""
    print("Stage 1: Discovering clients...")
    driver.get(PORTAL_URL)
    wait = WebDriverWait(driver, 20)
    
    # Login to reach selection
    wait.until(EC.presence_of_element_located((By.ID, "user_name"))).send_keys(USERNAME)
    driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
    driver.find_element(By.ID, "btnLogin").click()

    # Trigger dropdown with a broad search
    client_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text']")))
    client_input.click()
    client_input.send_keys("Adventist") 
    time.sleep(5) 

    suggestions = driver.find_elements(By.XPATH, "//ul/li | //li[contains(@class, 'item')]")
    discovered = [s.text.strip() for s in suggestions if s.text.strip()]
    print(f"Discovered {len(discovered)} clients.")
    return discovered

def scrape_client(client_name):
    """Stage 2: Process a client using JS injection to prevent the 'Blank Box' error."""
    excel_file = get_valid_filename(client_name)
    print(f"\n--- Processing: {client_name} ---")

    try:
        driver.get(PORTAL_URL)
        wait = WebDriverWait(driver, 20)
        
        # Login
        wait.until(EC.presence_of_element_located((By.ID, "user_name"))).send_keys(USERNAME)
        driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
        driver.find_element(By.ID, "btnLogin").click()

        # Input and Click via JS to ensure event binding
        client_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text']")))
        client_input.click()
        client_input.clear()
        
        for char in client_name:
            client_input.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(3) 

        # KEY FIX: Using JS to find the element and dispatch events that Selenium .click() sometimes misses
        try:
            # Find the first visible suggestion
            suggestion_xpath = f"//li[text()='{client_name}'] | //ul/li[1]"
            suggestion = wait.until(EC.presence_of_element_located((By.XPATH, suggestion_xpath)))
            
            # Dispatch multiple events to satisfy ASP.NET validation
            js_click = """
            var el = arguments[0];
            var evts = ['mousedown', 'mouseup', 'click', 'change'];
            evts.forEach(function(e){
                var evt = document.createEvent('HTMLEvents');
                evt.initEvent(e, true, true);
                el.dispatchEvent(evt);
            });
            """
            driver.execute_script(js_click, suggestion)
            print("Selection events dispatched via JS.")
        except:
            client_input.send_keys(Keys.ARROW_DOWN)
            client_input.send_keys(Keys.ENTER)

        time.sleep(2)
        # Final check if box is still filled before clicking Continue
        driver.find_element(By.XPATH, "//*[contains(@id, 'Continue') or @value='Continue']").click()

        # Scrape Table
        time.sleep(5)
        driver.get(JOBS_URL)
        new_jobs = []
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            rows = driver.find_elements(By.XPATH, "//tr[td]")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                d = [c.text.strip() for c in cells if c.text.strip()]
                if d:
                    new_jobs.append({"JOD #": d[0], "Status": d[1], "Position": d[5], "Dept": d[6]})
        except:
            print(f"Notice: No jobs for {client_name}")

        # Sync Excel
        if new_jobs:
            df_new = pd.DataFrame(new_jobs)
            if os.path.exists(excel_file):
                df_old = pd.read_excel(excel_file)
                df_old['JOD #'] = df_old['JOD #'].astype(str)
                df_new['JOD #'] = df_new['JOD #'].astype(str)
                df_final = df_new.set_index('JOD #').combine_first(df_old.set_index('JOD #')).reset_index()
                df_final.update(df_new.set_index('JOD #'))
            else:
                df_final = df_new
            df_final.to_excel(excel_file, index=False)
            print(f"SUCCESS: Synced to {excel_file}")

    except Exception as e:
        print(f"Skipping {client_name} due to unexpected screen state.")

# RUN
try:
    all_clients = get_dynamic_client_list()
    for c in all_clients:
        scrape_client(c)
finally:
    driver.quit()
