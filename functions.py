import os
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ----- Driver (explicit path + headless + SwiftShader) -----

def _pick_chromedriver_path() -> str:
    p = os.getenv("CHROMEDRIVER")
    if p and Path(p).is_file():
        return p
    if sys.platform.startswith("win"):
        candidates = [
            r"C:\tools\chromedriver\chromedriver.exe",
            r"C:\Program Files\ChromeDriver\chromedriver.exe",
            r"C:\Program Files (x86)\ChromeDriver\chromedriver.exe",
        ]
    elif sys.platform.startswith("linux"):
        candidates = ["/usr/bin/chromedriver", "/usr/local/bin/chromedriver"]
    else:  # macOS
        candidates = ["/opt/homebrew/bin/chromedriver", "/usr/local/bin/chromedriver"]
    for c in candidates:
        if Path(c).is_file():
            return c
    raise FileNotFoundError("Set CHROMEDRIVER to your chromedriver path.")

def start_driver(headless: bool = True) -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,800")
    # WebGL/SwiftShader deprecation fix
    opts.add_argument("--enable-unsafe-swiftshader")
    opts.add_argument("--use-angle=swiftshader")
    # proxy / tls (remove if not needed)
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--allow-insecure-localhost")

    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin and Path(chrome_bin).is_file():
        opts.binary_location = chrome_bin

    service = Service(executable_path=_pick_chromedriver_path())
    return webdriver.Chrome(service=service, options=opts)


# ----- Element helpers (ID or CSS + iframes + robust typing) -----

def _is_css(selector: str) -> bool:
    # Treat as CSS if it starts with # or contains CSSy chars
    return selector.startswith("#") or any(s in selector for s in [".", "[", " ", ">", "=", ":"])

def _find_element(driver, wait, selector: str):
    """
    Try to find element by ID or CSS in the main doc; if not found,
    iterate iframes and retry.
    """
    def _try_here():
        try:
            if _is_css(selector):
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            else:
                return wait.until(EC.presence_of_element_located((By.ID, selector)))
        except Exception:
            return None

    # default content
    driver.switch_to.default_content()
    el = _try_here()
    if el:
        return el

    # search iframes
    frames = driver.find_elements(By.CSS_SELECTOR, "iframe, frame")
    for idx in range(len(frames)):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(idx)
            el = _try_here()
            if el:
                return el
        except Exception:
            continue

    driver.switch_to.default_content()
    return None

def _robust_type(driver, el, text: str):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.click()
    except Exception:
        pass
    try:
        el.clear()
    except Exception:
        # Fallback clear: Ctrl/Meta+A then Backspace
        from selenium.webdriver.common.keys import Keys
        try:
            el.send_keys(Keys.CONTROL, "a")
        except Exception:
            el.send_keys(Keys.COMMAND, "a")
        el.send_keys("\b")
    el.send_keys(text)


# ----- Public flows -----

def fill_only(url, username, password, user_field_selector, pass_field_selector, wait_time=15, headless=True):
    """
    user_field_selector & pass_field_selector can be either an element ID (e.g. "username")
    or a CSS selector (e.g. "#username", "input[name='email']").
    """
    driver = start_driver(headless=headless)
    driver.set_page_load_timeout(30)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, wait_time)

        user_el = _find_element(driver, wait, user_field_selector)
        pass_el = _find_element(driver, wait, pass_field_selector)
        if not user_el or not pass_el:
            raise RuntimeError("Could not find username/password field. Try passing CSS selectors.")

        _robust_type(driver, user_el, username)
        _robust_type(driver, pass_el, password)

        time.sleep(1.0)
        return {"ok": True, "message": "Fields filled, not submitted", "current_url": driver.current_url}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        driver.quit()

def do_login(url, username, password, user_field_selector, pass_field_selector, login_button_selector, wait_time=15, headless=True):
    driver = start_driver(headless=headless)
    driver.set_page_load_timeout(30)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, wait_time)

        user_el = _find_element(driver, wait, user_field_selector)
        pass_el = _find_element(driver, wait, pass_field_selector)
        if not user_el or not pass_el:
            raise RuntimeError("Could not find username/password field. Try passing CSS selectors.")

        _robust_type(driver, user_el, username)
        _robust_type(driver, pass_el, password)

        # Find login button (ID or CSS, with iframe fallback)
        btn_el = _find_element(driver, wait, login_button_selector)
        if not btn_el:
            raise RuntimeError("Could not find login button. Provide a CSS selector if ID fails.")

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_el)
        try:
            btn_el.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn_el)

        time.sleep(1.5)

        # Optional: read a common message area
        message = ""
        for sel in ["#flash", ".flash", ".alert", ".notification", "[role='alert']"]:
            el = _find_element(driver, WebDriverWait(driver, 1), sel)
            if el:
                txt = (el.text or "").strip()
                if txt:
                    message = txt
                    break

        return {"ok": True, "message": message, "current_url": driver.current_url}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        driver.quit()