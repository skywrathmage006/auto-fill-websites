import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    import keyring
except ImportError:
    keyring = None

APP = "herokuapp_login"

# Retrieve secret
def get_secret(app, key, env_fallback):
    if keyring:
        v = keyring.get_password(app, key)
        if v:
            return v
    return os.getenv(env_fallback)

USERNAME = os.getenv("HEROKUAPP_USER") or "tomsmith"  # default test user
PASSWORD = get_secret(APP, "password", "HEROKUAPP_PASSWORD") or "SuperSecretPassword!"

# Start Selenium
driver = webdriver.Chrome()  # Make sure ChromeDriver is installed
driver.get("https://the-internet.herokuapp.com/login")

wait = WebDriverWait(driver, 10)
user_box = wait.until(EC.presence_of_element_located((By.ID, "username")))
pass_box = wait.until(EC.presence_of_element_located((By.ID, "password")))
login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]")))

# Fill in fields
user_box.clear(); user_box.send_keys(USERNAME)
pass_box.clear(); pass_box.send_keys(PASSWORD)

# Click login
login_btn.click()

# Optional: print result
message = wait.until(EC.presence_of_element_located((By.ID, "flash"))).text
print("Login message:", message)

# Keep browser open for 5 seconds to see result
import time; time.sleep(5)
driver.quit()
