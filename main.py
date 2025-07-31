import os
import shutil
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# 🔐 Replace with real data
SESSIONID = "your_sessionid_here"
CSRFTOKEN = "your_csrftoken_here"
TARGET_USERNAME = "target_username_here"

def find_chrome_binary():
    # Common binary paths
    possible_paths = [
        shutil.which("google-chrome"),
        shutil.which("chrome"),
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    return None

def report_user(sessionid, csrftoken, username):
    chrome_path = find_chrome_binary()
    if not chrome_path:
        print("❌ Chrome browser not found. Please install it.")
        return

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.binary_location = chrome_path  # ✅ Auto-detected path

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

        # Try final confirmation
        try:
            final = driver.find_element(By.XPATH, "//button/div[contains(text(),'Submit') or contains(text(),'Done')]")
            final.click()
            time.sleep(2)
        except:
            pass

        print(f"✅ Report for @{username} submitted successfully.")

    except Exception as e:
        print(f"❌ Failed to report @{username}: {e}")
    finally:
        driver.quit()

# Run the tool
report_user(SESSIONID, CSRFTOKEN, TARGET_USERNAME)
