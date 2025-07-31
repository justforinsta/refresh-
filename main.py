import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# 🔐 Replace these with your real session credentials and target
SESSIONID = "your_sessionid_here"
CSRFTOKEN = "your_csrftoken_here"
TARGET_USERNAME = "target_username_here"

def report_user(sessionid, csrftoken, username):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = uc.Chrome(options=options)

    try:
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        driver.delete_all_cookies()

        # Set cookies for session login
        driver.add_cookie({"name": "sessionid", "value": sessionid, "domain": ".instagram.com"})
        driver.add_cookie({"name": "csrftoken", "value": csrftoken, "domain": ".instagram.com"})

        driver.refresh()
        time.sleep(5)

        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(5)

        # Open 3-dot menu
        menu = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Options')]")
        menu.click()
        time.sleep(2)

        # Click "Report"
        report = driver.find_element(By.XPATH, "//button/div[text()='Report']")
        report.click()
        time.sleep(2)

        # Click "Report account"
        report_account = driver.find_element(By.XPATH, "//button/div[text()='Report account']")
        report_account.click()
        time.sleep(2)

        # Select "It's pretending to be someone else"
        pretending = driver.find_element(By.XPATH, "//button/div[contains(text(),'pretending')]")
        pretending.click()
        time.sleep(2)

        # If there's a final Submit or Done button, click it
        try:
            final = driver.find_element(By.XPATH, "//button/div[contains(text(),'Submit') or contains(text(),'Done')]")
            final.click()
            time.sleep(2)
        except:
            pass

        print(f"✅ Reported @{username} successfully.")
    except Exception as e:
        print(f"❌ Failed to report @{username}: {e}")
    finally:
        driver.quit()

# Run it
report_user(SESSIONID, CSRFTOKEN, TARGET_USERNAME)
