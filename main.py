import time
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# 👉 Update these values
SESSIONID = "your_sessionid_here"
CSRFTOKEN = "your_csrftoken_here"
TARGET_USERNAME = "target_username_here"

def report_user(sessionid, csrftoken, username):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)

    driver.get("https://www.instagram.com/")
    driver.delete_all_cookies()

    # Set cookies
    driver.add_cookie({"name": "sessionid", "value": sessionid, "domain": ".instagram.com"})
    driver.add_cookie({"name": "csrftoken", "value": csrftoken, "domain": ".instagram.com"})

    driver.refresh()
    time.sleep(5)

    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

    try:
        # Click the 3-dot options menu
        menu_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Options')]")
        menu_button.click()
        time.sleep(2)

        # Click "Report"
        report_button = driver.find_element(By.XPATH, "//button/div[text()='Report']")
        report_button.click()
        time.sleep(2)

        # Select "Report Account"
        driver.find_element(By.XPATH, "//button/div[text()='Report account']").click()
        time.sleep(2)

        # Select "It's pretending to be someone else"
        driver.find_element(By.XPATH, "//button/div[contains(text(),'pretending')]").click()
        time.sleep(2)

        # Finalize (Instagram may vary this step)
        driver.find_element(By.XPATH, "//button/div[contains(text(),'Submit')]").click()
        time.sleep(2)

        print(f"✅ Report for @{username} submitted successfully.")

    except Exception as e:
        print(f"❌ Failed to report @{username}: {e}")

    driver.quit()

# Run it
report_user(SESSIONID, CSRFTOKEN, TARGET_USERNAME)
