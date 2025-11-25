from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import random

import time
import os



def human_type(element, text):
    for char in text:
        time.sleep(random.randint(1,2)) 
        element.send_keys(char)

options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.cp.pt/pt/")

try:

    load_dotenv()
    CP_PASSWORD = os.getenv('CP_PASSWORD')
    CP_USERNAME = os.getenv('CP_USERNAME')
    cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    cookie_button.click()
    my_cp_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary'][.//img[@alt='profile']]"))
    )
    my_cp_button.click()

    my_cp_username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    my_cp_password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )

    human_type(my_cp_username,CP_USERNAME)
    human_type(my_cp_password,CP_PASSWORD)

 


    cp_login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "kc-login"))
    )
    cp_login_button.click()

    time.sleep(10)

        


    
except Exception as e:
    print(f"Error: {e}")


driver.close()
