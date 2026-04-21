from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import argparse
import os

# ── Helpers ───────────────────────────────────────────────────────────────────

def wait_and_click(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    ).click()

def wait_for_all(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )
def mount_url(departure_station,arrival_station):
    # Navigate to search results
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    url = (
        f"https://cp.pt/pt/resultado-pesquisa?"
        f"passageiros=1&selectedClass=2"
        f"&startDate={tomorrow}"
        f"&departureStation={departure_station}"
        f"&arrivalStation={arrival_station}"
    )
    return url

# ── Driver setup ──────────────────────────────────────────────────────────────

def build_driver():
    options = Options()
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

# ── Main flow ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('origin')
    parser.add_argument('destination')
    parser.add_argument('departure')
    parser.add_argument('arrival')
    args = parser.parse_args()

    load_dotenv()
    CP_USERNAME             = os.getenv('CP_USERNAME')
    CP_PASSWORD             = os.getenv('CP_PASSWORD')
    PASSE_VERDE             = os.getenv('PASSE_VERDE')
    DEPARTURE_TIME          = args.departure
    ARRIVAL_TIME            = args.arrival
    DEPARTURE_STATION       = args.origin
    ARRIVAL_STATION         = args.destination

    driver = build_driver()
    driver.get("https://www.cp.pt/pt/")

    try:
        # Accept cookies
        wait_and_click(driver, By.ID, "onetrust-accept-btn-handler")

        # Open login
        wait_and_click(driver, By.XPATH,
            "//button[@class='btn btn-primary'][.//img[@alt='profile']]"
        )

        # Fill credentials
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(CP_USERNAME)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        ).send_keys(CP_PASSWORD)

        wait_and_click(driver, By.ID, "kc-login")

        driver.get(mount_url(DEPARTURE_STATION,ARRIVAL_STATION))

        wait_and_click(driver, By.XPATH,
            f'//button[@aria-label="Selecionar ida das {DEPARTURE_TIME} às {ARRIVAL_TIME}"]'
        )

        # Checkout steps
        wait_and_click(driver, By.XPATH, '//*[@id="buyTripNavBar"]/div[2]/button')
        wait_and_click(driver, By.XPATH, '//*[@id="main"]/div/div[3]/div/div[3]/div[2]/label/span')
        wait_and_click(driver, By.XPATH, '//*[@id="main"]/div/div[3]/div/div[3]/button')


        comboboxes = wait_for_all(driver, By.CSS_SELECTOR, '[role="combobox"]')
        
        comboboxes[1].click()

        dropdown_options = wait_for_all(driver, By.CSS_SELECTOR, '[role="option"]')
       
        dropdown_options[2].click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "discountInputValue"))
        ).send_keys(PASSE_VERDE)

        wait_and_click(driver, By.XPATH, '//button[@type="submit"]')

        wait_and_click(driver, By.CSS_SELECTOR, '.confirm-places-data__submit .button-custom-primary')
        wait_and_click(driver, By.CSS_SELECTOR, '.modal-confirmation-place__nextBtn')
        wait_and_click(driver, By.CSS_SELECTOR, '.passenger-data__submit .button-custom-primary')


        time.sleep(10)
    
    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()