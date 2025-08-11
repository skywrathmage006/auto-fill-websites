import os
import sys
import time
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _pick_chromedriver_path() -> Optional[str]:
    """Return a valid chromedriver path if we can find one, else None."""
    # 1) Explicit env override
    env_path = os.getenv("CHROMEDRIVER")
    if env_path and Path(env_path).is_file():
        return env_path

    # 2) OS-specific defaults
    if sys.platform.startswith("win"):
        candidates = [
            r"C:\tools\chromedriver\chromedriver.exe",
            r"C:\Program Files\ChromeDriver\chromedriver.exe",
            r"C:\Program Files (x86)\ChromeDriver\chromedriver.exe",
        ]
    elif sys.platform.startswith("linux"):
        candidates = ["/usr/bin/chromedriver", "/usr/local/bin/chromedriver"]
    else:  # macOS (darwin)
        candidates = ["/opt/homebrew/bin/chromedriver", "/usr/local/bin/chromedriver"]

    for p in candidates:
        if Path(p).is_file():
            return p

    # 3) None -> let Selenium Manager resolve automatically
    return None


def start_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Start Chrome. If a chromedriver binary is found (env or known paths), use it.
    Otherwise, let Selenium Manager auto-resolve.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")

    # Optional: point to Chromium/Chrome binary via env (useful in containers)
    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin and Path(chrome_bin).is_file():
        options.binary_location = chrome_bin

    driver_path = _pick_chromedriver_path()
    if driver_path:
        service = ChromeService(executable_path=driver_path)
        return webdriver.Chrome(service=service, options=options)
    else:
        # Fall back to Selenium Manager
        return webdriver.Chrome(options=options)


def fill_only(url, username, password, user_field_id, pass_field_id, wait_time=15, headless=True):
    """Open URL, fill credentials, but do not click login."""
    driver = start_driver(headless=headless)
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
    driver = start_driver(headless=headless)
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

        # Try to capture a visible flash/alert message
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