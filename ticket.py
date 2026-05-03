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
def print_page_text(driver):
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print("---- Page Text ----")
    print(body_text)
    print("-------------------")

def wait_and_click(driver, by, value, timeout=30):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    ).click()

def wait_for_all(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )

def mount_url(departure_station, arrival_station):
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.today().strftime('%Y-%m-%d')
    return (
        f"https://cp.pt/pt/resultado-pesquisa?"
        f"passageiros=1&selectedClass=2"
        f"&startDate={tomorrow}"
        f"&departureStation={departure_station}"
        f"&arrivalStation={arrival_station}"
    )

def build_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
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

def login(driver, username, password):
    wait_and_click(driver, By.XPATH,
        "//button[@class='btn btn-primary'][.//img[@alt='profile']]"
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    ).send_keys(username)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    ).send_keys(password)
    wait_and_click(driver, By.ID, "kc-login")

def wait_for_opening(departure_time, wait_for_opening):
    if not wait_for_opening:
        return
    open_time = datetime.strptime(departure_time, "%H:%M").replace(
        year=datetime.today().year,
        month=datetime.today().month,
        day=datetime.today().day
    )
    print(f"Waiting for ticket opening at {departure_time}...")
    while True:
        remaining = (open_time - datetime.now()).total_seconds()
        if remaining <= 0:
            break
        elif remaining > 60:
            print(f"  {int(remaining)}s remaining...", end="\r")
            time.sleep(10)
        elif remaining > 5:
            print(f"  {remaining:.1f}s remaining...", end="\r")
            time.sleep(1)
        else:
            print(f"  {remaining:.2f}s remaining...", end="\r")
            time.sleep(0.05)
    print("Tickets open! Proceeding...")

def apply_discount(driver, passe_verde):
    comboboxes = wait_for_all(driver, By.CSS_SELECTOR, '[role="combobox"]')
    comboboxes[1].click()
    dropdown_options = wait_for_all(driver, By.CSS_SELECTOR, '[role="option"]')
    dropdown_options[2].click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "discountInputValue"))
    ).send_keys(passe_verde)
    wait_and_click(driver, By.XPATH, '//button[@type="submit"]')

# ── Main flow ─────────────────────────────────────────────────────────────────

def main():
    screenshot_dir = os.path.expanduser("~/CP/TICKET_BUYER/")
    if not os.path.exists(screenshot_dir):
        print(f"Directory does not exist: {screenshot_dir}")
        return
    else:
        print(f"Directory exists: {screenshot_dir}")

    parser = argparse.ArgumentParser()
    parser.add_argument('origin')
    parser.add_argument('destination')
    parser.add_argument('departure')
    parser.add_argument('--wait', action='store_true')
    parser.add_argument('--retry', action='store_true')


    args = parser.parse_args()

    load_dotenv()
    CP_USERNAME       = os.getenv('CP_USERNAME')
    CP_PASSWORD       = os.getenv('CP_PASSWORD')
    PASSE_VERDE       = os.getenv('PASSE_VERDE')
    DEPARTURE_TIME    = args.departure
    DEPARTURE_STATION = args.origin
    ARRIVAL_STATION   = args.destination
    WAIT_FOR_OPENING  = args.wait
    RETRY_IF_FAILS    = args.retry


    missing = [name for name, val in {
        'CP_USERNAME':        CP_USERNAME,
        'CP_PASSWORD':        CP_PASSWORD,
        'PASSE_VERDE':        PASSE_VERDE,
        'DEPARTURE_TIME':     DEPARTURE_TIME,
        'DEPARTURE_STATION':  DEPARTURE_STATION,
        'ARRIVAL_STATION':    ARRIVAL_STATION,
    }.items() if not val]

    if missing:
        print(f"Missing: {', '.join(missing)}")
        return
    else :
        print(f"""
            Starting script with:
            Origin:      {DEPARTURE_STATION}
            Destination: {ARRIVAL_STATION}
            Departure:   {DEPARTURE_TIME}
            Open time:   {WAIT_FOR_OPENING}
            Username:    {CP_USERNAME}
        """)

    driver = build_driver()
    driver.get("https://www.cp.pt/pt/")

    try:
        wait_and_click(driver, By.ID, "onetrust-accept-btn-handler")

        login(driver, CP_USERNAME, CP_PASSWORD)

        time.sleep(1)
        driver.get(mount_url(DEPARTURE_STATION, ARRIVAL_STATION))

        wait_and_click(driver, By.XPATH,
            f'//button[contains(@aria-label, "Selecionar ida das {DEPARTURE_TIME}")]'
        )

        wait_and_click(driver, By.XPATH, '//*[@id="buyTripNavBar"]/div[2]/button')
        wait_and_click(driver, By.XPATH, '//*[@id="main"]/div/div[3]/div/div[3]/div[2]/label/span')
        wait_for_opening(DEPARTURE_TIME,WAIT_FOR_OPENING)

        wait_and_click(driver, By.XPATH, '//*[@id="main"]/div/div[3]/div/div[3]/button')

        apply_discount(driver, PASSE_VERDE)
        time.sleep(2)

        wait_and_click(driver, By.CSS_SELECTOR, '.confirm-places-data__submit .button-custom-primary')
        time.sleep(2)
        wait_and_click(driver, By.CSS_SELECTOR, '.modal-confirmation-place__nextBtn')
        time.sleep(2)
        wait_and_click(driver, By.CSS_SELECTOR, '.passenger-data__submit .button-custom-primary')
        time.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.save_screenshot(os.path.join(screenshot_dir, "finish.png"))
        print(f"Final screenshot saved to: {os.path.abspath(screenshot_dir)}finish.png")
        print_page_text(driver)
        driver.quit()

if __name__ == "__main__":
    main()