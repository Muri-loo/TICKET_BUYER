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
    my_cp_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary'][.//img[@alt='profile']]"))
    )
    
    print("Button found!")
    print("Button text:", my_cp_button.text)
    print("Button class:", my_cp_button.get_attribute('class'))
    print("Button HTML:", my_cp_button.get_attribute('outerHTML'))
    
    # Click it
    my_cp_button.click()
    
except Exception as e:
    print(f"Error: {e}")


driver.close()