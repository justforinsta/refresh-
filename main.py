import os
import shutil
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# 🔐 Replace with real Instagram session data
SESSIONID = "your_sessionid_here"
CSRFTOKEN = "your_csrftoken_here"
TARGET_USERNAME = "target_username_here"

def find_chrome_binary():
    paths = [
        shutil.which("google-chrome"),
        shutil.which("chrome"),
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    for path in paths:
        if path and os.path.exists(path):
            return path
    return None

def report_user(sessionid, csrftoken, username):
    chrome_path = find_chrome_binary()
    if not chrome_path:
        print("❌ Chrome browser not found. Please install Chrome.")
        return

    print(f"✅ Found Chrome at: {chrome_path}")

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = chrome_path  # ✅ Safe binary location assignment

    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"❌ Failed to launch Chrome: {e}")
        return

    try:
        print("🌐 Opening Instagram...")
        driver.get("https://www.instagram.com/")
        time.sleep(3)

        print("🍪 Injecting session cookies...")
        driver.delete_all_cookies()
        driver.add_cookie({"name": "sessionid", "value": sessionid, "domain": ".instagram.com"})
        driver.add_cookie({"name": "csrftoken", "value": csrftoken, "domain": ".instagram.com"})

        print("🔄 Refreshing with session...")
        driver.refresh()
        time.sleep(5)

        print(f"👀 Visiting: https://www.instagram.com/{username}/")
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(5)

        print("📸 Screenshot saved as screenshot.png")
        driver.save_screenshot("screenshot.png")

    except Exception as e:
        print(f"❌ Error during automation: {e}")
    finally:
        driver.quit()
        print("🧹 Chrome closed.")

# 🚀 Run
report_user(SESSIONID, CSRFTOKEN, TARGET_USERNAME)
