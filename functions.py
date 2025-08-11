import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

# Automatically install the correct ChromeDriver version
chromedriver_autoinstaller.install()

def start_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def fill_only(url, username, password, user_field_id, pass_field_id, wait_time=15, headless=True):
    """Open URL, fill credentials, but do not click login."""
    driver = start_driver(headless)
    driver.set_page_load_timeout(30)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, wait_time)

        user_box = wait.until(EC.presence_of_element_located((By.ID, user_field_id)))
        user_box.clear()
        user_box.send_keys(username)

        pass_box = wait.until(EC.presence_of_element_located((By.ID, pass_field_id)))
        pass_box.clear()
        pass_box.send_keys(password)

        time.sleep(2)
        return {"ok": True, "message": "Fields filled, not submitted", "current_url": driver.current_url}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        driver.quit()

def do_login(url, username, password, user_field_id, pass_field_id, login_button_selector, wait_time=15, headless=True):
    """Open URL, fill credentials, click login."""
    driver = start_driver(headless)
    driver.set_page_load_timeout(30)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, wait_time)

        user_box = wait.until(EC.presence_of_element_located((By.ID, user_field_id)))
        user_box.clear()
        user_box.send_keys(username)

        pass_box = wait.until(EC.presence_of_element_located((By.ID, pass_field_id)))
        pass_box.clear()
        pass_box.send_keys(password)

        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_selector)))
        login_btn.click()

        time.sleep(1.5)

        message = ""
        for sel in ["#flash", ".flash", ".alert", ".notification", "[role='alert']"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el and el.text.strip():
                    message = el.text.strip()
                    break
            except Exception:
                pass

        return {"ok": True, "message": message, "current_url": driver.current_url}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        driver.quit()