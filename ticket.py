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

my_cp_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[.//img[@alt='profile']]"))
)

driver.get("https://www.cp.pt/pt/")
print("Opened: " + driver.title)
driver.close()