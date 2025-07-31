import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# 🔐 Replace with your actual values
SESSIONID = "your_sessionid_here"
CSRFTOKEN = "your_csrftoken_here"
TARGET_USERNAME = "target_username_here"

def report_user(sessionid, csrftoken, username):
    print("📦 Starting Chrome...")
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    driver = uc.Chrome(options=options)

    try:
        print("🌐 Opening Instagram...")
        driver.get("https://www.instagram.com/")
        time.sleep(3)

        print("🍪 Injecting session cookies...")
        driver.delete_all_cookies()
        driver.add_cookie({"name": "sessionid", "value": sessionid, "domain": ".instagram.com"})
        driver.add_cookie({"name": "csrftoken", "value": csrftoken, "domain": ".instagram.com"})

        print("🔄 Refreshing to apply session...")
        driver.refresh()
        time.sleep(5)

        print(f"👀 Navigating to target profile: @{username}")
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(5)

        print("📸 Taking screenshot...")
        driver.save_screenshot("screenshot.png")
        print("✅ Screenshot saved as screenshot.png")

        # Optional: uncomment this to continue to report steps
        # print("📎 Opening menu...")
        # menu = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Options')]")
        # menu.click()
        # time.sleep(2)

        # print("🚨 Clicking 'Report'...")
        # report = driver.find_element(By.XPATH, "//button/div[text()='Report']")
        # report.click()
        # time.sleep(2)

        # Add additional reporting steps here if needed...

    except Exception as e:
        print(f"❌ Error occurred: {e}")
    finally:
        time.sleep(2)
        driver.quit()
        print("🧹 Browser closed.")

# 🚀 Run it
report_user(SESSIONID, CSRFTOKEN, TARGET_USERNAME)
