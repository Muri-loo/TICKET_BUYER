from dotenv import load_dotenv
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import argparse
import os
import undetected_chromedriver as uc

# VARS
TIMEOUT_VALUE = 30
TIME_FOR_RETRY_AGAIN = 120


# ?? Helpers ???????????????????????????????????????????????????????????????????
def print_page_text(driver):
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print("---- Page Text ----")
    print(body_text)
    print("-------------------")


def wait_and_click(driver, by, value, timeout=TIMEOUT_VALUE, label=None):
    tag = label or value
    print(f"  [click] Waiting for: {tag}")
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    print(f"  [click] Found & clicking: {tag}")
    el.click()
    print(f"  [click] Done: {tag}")


def wait_for_all(driver, by, value, timeout=TIMEOUT_VALUE):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by, value))
    )


def mount_url(departure_station, arrival_station):
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.today().strftime('%Y-%m-%d')
    url = (
        f"https://cp.pt/pt/resultado-pesquisa?"
        f"passageiros=1&selectedClass=2"
        f"&startDate={tomorrow}"
        f"&departureStation={departure_station}"
        f"&arrivalStation={arrival_station}"
    )
    print(f"  [url] Built URL: {url}")
    return url


def build_driver():
    print("[driver] Building undetected driver...")
    options = uc.ChromeOptions()
    # options.add_argument("--user-data-dir=/home/murilo-oliveira/CP/chrome-profile")
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    driver = uc.Chrome(options=options)
    print("[driver] Driver ready.")
    return driver


def login(driver, username, password):
    print("[login] Starting login flow...")
    wait_and_click(driver, By.XPATH,
                   "//button[@class='btn btn-primary'][.//img[@alt='profile']]",
                   label="profile button")
    print("[login] Entering username...")
    WebDriverWait(driver, TIMEOUT_VALUE).until(
        EC.presence_of_element_located((By.ID, "username"))
    ).send_keys(username)
    print("[login] Entering password...")
    WebDriverWait(driver, TIMEOUT_VALUE).until(
        EC.presence_of_element_located((By.ID, "password"))
    ).send_keys(password)
    print("[login] Submitting login form...")
    wait_and_click(driver, By.ID, "kc-login", label="kc-login button")
    print("[login] Login submitted.")


def wait_for_opening(departure_time, wait_for_opening):
    if not wait_for_opening:
        print("[wait] Skipping wait for opening (--wait not set).")
        return
    open_time = datetime.strptime(departure_time, "%H:%M").replace(
        year=datetime.today().year,
        month=datetime.today().month,
        day=datetime.today().day
    )
    print(f"[wait] Waiting for ticket opening at {departure_time}...")
    while True:
        remaining = (open_time - datetime.now()).total_seconds()
        if remaining <= 0:
            break
        elif remaining > 60:
            print(f"  [wait] {int(remaining)}s remaining...", end="\r")
            time.sleep(10)
        elif remaining > 5:
            print(f"  [wait] {remaining:.1f}s remaining...", end="\r")
            time.sleep(1)
        else:
            print(f"  [wait] {remaining:.2f}s remaining...", end="\r")
            time.sleep(0.05)
    print("\n[wait] Tickets open! Proceeding...")


def apply_discount(driver, passe_verde):
    print("[discount] Applying Passe Verde discount...")
    combo_boxes = wait_for_all(driver, By.CSS_SELECTOR, '[role="combobox"]')
    print(f"[discount] Found {len(combo_boxes)} combobox(es). Clicking second one...")
    combo_boxes[1].click()
    dropdown_options = wait_for_all(driver, By.CSS_SELECTOR, '[role="option"]')
    print(f"[discount] Found {len(dropdown_options)} dropdown option(s). Selecting option[2]...")
    dropdown_options[1].click()
    print("[discount] Entering Passe Verde number...")
    WebDriverWait(driver, TIMEOUT_VALUE).until(
        EC.presence_of_element_located((By.NAME, "discountInputValue"))
    ).send_keys(passe_verde)
    print("[discount] Submitting discount form...")
    wait_and_click(driver, By.XPATH, '//button[@type="submit"]', label="discount submit")
    print("[discount] Discount applied.")


def buy_attempt(driver, DEPARTURE_TIME, WAIT_FOR_OPENING):
    print(f"[buy] Step 1/3 — Selecting departure time: {DEPARTURE_TIME}")
    wait_and_click(driver, By.XPATH,
                   f'//button[contains(@aria-label, "Selecionar ida das {DEPARTURE_TIME}")]'
                   )

    print("[buy] Step 2/3 — Clicking next in nav bar...")
    wait_and_click(driver, By.XPATH, '//*[@id="buyTripNavBar"]/div[2]/button',
                   label="buyTripNavBar next")

    print("[buy] Step 3/3 — Selecting ticket type (label/span)...")
    wait_and_click(driver, By.XPATH, '//*[@id="main"]/div/div[3]/div/div[3]/div[2]/label/span',
                   label="ticket type selector")

    wait_for_opening(DEPARTURE_TIME, WAIT_FOR_OPENING)

    print("[buy] Clicking final confirm button...")
    wait_and_click(driver, By.XPATH, '//*[@id="main"]/div/div[3]/div/div[3]/button',
                   label="confirm buy button")
    print("[buy] buyAttempt complete.")


def try_accept_cookies(driver):
    print("[cookies] Trying to accept cookies...")
    try:
        wait_and_click(driver, By.ID, "onetrust-accept-btn-handler", timeout=3,
                       label="cookie accept button")
        print("[cookies] Cookies accepted.")
    except:
        print("[cookies] No cookie banner found (or already accepted).")


def buy_attempt_with_retry(driver, DEPARTURE_TIME, WAIT_FOR_OPENING, retry_delay=TIME_FOR_RETRY_AGAIN):
    failed_words = ["esgotado", "cheio", "disponíveis", "reveja"]
    while True:
        buy_attempt(driver, DEPARTURE_TIME, WAIT_FOR_OPENING)
        time.sleep(5)
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        if not any(word in body_text for word in failed_words):
            print("[retry] Success — no failure words found. Proceeding.")
            break
        print(f"[retry] Failed words detected in page, retrying in {retry_delay}s...")
        driver.back()
        time.sleep(retry_delay)


# ?? Main flow ?????????????????????????????????????????????????????????????????

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
    CP_USERNAME = os.getenv('CP_USERNAME')
    CP_PASSWORD = os.getenv('CP_PASSWORD')
    PASSE_VERDE = os.getenv('PASSE_VERDE')
    DEPARTURE_TIME = args.departure
    DEPARTURE_STATION = args.origin
    ARRIVAL_STATION = args.destination
    WAIT_FOR_OPENING = args.wait
    RETRY_IF_FAILS = args.retry

    missing = [name for name, val in {
        'CP_USERNAME': CP_USERNAME,
        'CP_PASSWORD': CP_PASSWORD,
        'PASSE_VERDE': PASSE_VERDE,
        'DEPARTURE_TIME': DEPARTURE_TIME,
        'DEPARTURE_STATION': DEPARTURE_STATION,
        'ARRIVAL_STATION': ARRIVAL_STATION,
    }.items() if not val]

    if missing:
        print(f"Missing: {', '.join(missing)}")
        return
    else:
        print(f"""
                Starting script with:
                Origin:      {DEPARTURE_STATION}
                Destination: {ARRIVAL_STATION}
                Departure:   {DEPARTURE_TIME}
                Open time:   {WAIT_FOR_OPENING}
                Username:    {CP_USERNAME}
                Retry:       {RETRY_IF_FAILS}
                Wait:        {WAIT_FOR_OPENING}
            """)

    print("[main] Building driver and opening CP homepage...")
    driver = build_driver()
    driver.get("https://www.cp.pt/pt/")
    print("[main] CP homepage loaded.")

    try:
        try_accept_cookies(driver)
        login(driver, CP_USERNAME, CP_PASSWORD)

        print("[main] Navigating to search results page...")
        time.sleep(5)
        driver.get(mount_url(DEPARTURE_STATION, ARRIVAL_STATION))
        print("[main] Search results page loaded.")
        if RETRY_IF_FAILS:
            retry_delay = 5 if WAIT_FOR_OPENING else TIME_FOR_RETRY_AGAIN
            buy_attempt_with_retry(driver, DEPARTURE_TIME, WAIT_FOR_OPENING, retry_delay=retry_delay)
        else:
            buy_attempt(driver, DEPARTURE_TIME, WAIT_FOR_OPENING)

        apply_discount(driver, PASSE_VERDE)

        print("[main] Sleeping 2s after discount...")
        time.sleep(2)

        print("[main] Clicking confirm places submit...")
        wait_and_click(driver, By.CSS_SELECTOR,
                       '.confirm-places-data__submit .button-custom-primary',
                       label="confirm places submit")
        time.sleep(2)

        print("[main] Clicking modal confirmation next...")
        wait_and_click(driver, By.CSS_SELECTOR,
                       '.modal-confirmation-place__nextBtn',
                       label="modal next button")
        time.sleep(2)

        print("[main] Clicking passenger data submit...")
        wait_and_click(driver, By.CSS_SELECTOR,
                       '.passenger-data__submit .button-custom-primary',
                       label="passenger data submit")

        print("[main] Waiting 10s for final processing...")
        time.sleep(10)
        print("[main] Done! Ticket should be purchased.")

    except Exception as e:
        print(f"[ERROR] Exception caught: {e}")
        import traceback
        traceback.print_exc()

    finally:
        screenshot_path = os.path.join(screenshot_dir, "finish.png")
        driver.save_screenshot(screenshot_path)
        print(f"[main] Final screenshot saved to: {os.path.abspath(screenshot_path)}")
        print_page_text(driver)
        driver.quit()


if __name__ == "__main__":
    main()
