from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


import time
import os

options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.cp.pt/pt/")

try:

    cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    cookie_button.click()
    my_cp_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary'][.//img[@alt='profile']]"))
    )
    my_cp_button.click()
    time.sleep(10)

    
except Exception as e:
    print(f"Error: {e}")


driver.close()

# This file was commented by Github Copilot!