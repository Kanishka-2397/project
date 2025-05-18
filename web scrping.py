import os
import json
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# -------------------- Configuration -------------------- #
config_samsung = {
    "model_id": ".ModelInfo_modalInfo__Dlls0 span",
    "title": "div.ProductTitle_product__KGKRj h1",
    "breadcrumb": ".Breadcrumb_breadcrumbText__WEmi6",
    "images": "img[src*='samsung.com']",
    "manual_link": "a[href$='.pdf']",
    "icon_features": ".ProductDetailsBadge_badge__wInap",
    "key_features": ".KeyFeatures_cards__V77Wy > div",
    "detailed_features": ".ProductSummary_detailList__3pjAV"
}

# -------------------- Playwright Search -------------------- #
def run_playwright_search(model_id, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto("https://www.samsung.com/us/")
        page.wait_for_load_state("load")

        try:
            consent_button = page.locator("button:has-text('Accept')").first
            if consent_button and consent_button.is_visible():
                consent_button.click(timeout=3000)
        except Exception:
            pass

        try:
            search_button = page.locator("div.nv00-gnb-v3__utility.search button[aria-label='Search']")
            search_button.click()
            page.wait_for_selector("input#gnb-search-keyword")
            search_input = page.locator("input#gnb-search-keyword")
            search_input.fill(model_id)
            search_input.press("Enter")
            page.wait_for_selector(".ProductCard__prodLink___3CTY0", timeout=15000)
            product_url = page.locator(".ProductCard__prodLink___3CTY0").first.get_attribute("href")
            return urljoin("https://www.samsung.com/us", product_url) if product_url else None
        except Exception as e:
            print(f"[ERROR] Playwright search failed: {e}")
            return None
        finally:
            browser.close()

# -------------------- Selenium Setup -------------------- #
def get_selenium_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -------------------- Scraping Functions -------------------- #
def fetch_page_data(driver, url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config_samsung["title"]))
            )
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return driver.page_source
        except TimeoutException:
            print(f"[WARN] Timeout loading page, retrying ({attempt+1}/{retries})...")
        except Exception as e:
            print(f"[ERROR] Error during fetch: {e}")
    return None

def extract_product_data(html, config):
    soup = BeautifulSoup(html, "html.parser")

    def select_data(selector, attr=None, multiple=False):
        elements = soup.select(selector)
        if not elements:
            return [] if multiple else ""
        if multiple:
            values = []
            for el in elements:
                val = el.get(attr) if attr else el.get_text(strip=True)
                if val:
                    values.append(val)
            return list(dict.fromkeys(values))  # remove duplicates
        return elements[0].get(attr) if attr else elements[0].get_text(strip=True)

    model_id = select_data(config["model_id"])
    title = select_data(config["title"])
    breadcrumb_items = soup.select(config["breadcrumb"])
    category = " > ".join(item.get_text(strip=True) for item in breadcrumb_items)

    # Manual link
    manual_url = ""
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.lower().endswith(".pdf") and ("manual" in href.lower() or "user" in href.lower()):
            manual_url = urljoin("https://www.samsung.com/us", href)
            break
    if not manual_url:
        fallback = soup.select_one(config["manual_link"])
        if fallback and fallback.get("href", "").endswith(".pdf"):
            manual_url = urljoin("https://www.samsung.com/us", fallback["href"])

    # Images
    raw_image_urls = select_data(config["images"], attr="src", multiple=True)
    image_urls = [urljoin("https://www.samsung.com", src) if src.startswith("//") else src for src in raw_image_urls]

    icon_features = select_data(config["icon_features"], multiple=True)
    detailed_features = select_data(config["detailed_features"], multiple=True)
    key_features = select_data(config["key_features"], multiple=True)

    all_features = icon_features + key_features + detailed_features

    return model_id, title, all_features, image_urls, manual_url, category

def save_data_to_json(data, filename="samsung_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[DONE] Data saved to {filename}")

# -------------------- Main Execution -------------------- #
if __name__ == "__main__":
    headless_mode = True
    driver = get_selenium_driver(headless=headless_mode)

    model_input = input("Enter Samsung model IDs (comma-separated): ").strip()
    model_ids = [m.strip() for m in model_input.split(",") if m.strip()]

    if not model_ids:
        print("❌ No model IDs entered. Exiting.")
        exit(1)

    all_data = []

    try:
        for idx, model in enumerate(model_ids, 1):
            print(f"\n🔍 ({idx}/{len(model_ids)}) Searching for model: {model}")
            product_url = run_playwright_search(model, headless=headless_mode)
            if not product_url:
                print(f"[ERROR] No product found for model: {model}")
                continue

            html = fetch_page_data(driver, product_url)
            if not html:
                print(f"[ERROR] Failed to fetch HTML for model: {model}")
                continue

            model_id, title, features, images, manual, category = extract_product_data(html, config_samsung)

            all_data.append({
                "manufacturer": "Samsung",
                "model_id": model_id or model,
                "title": title,
                "category": category,
                "key_features": features,
                "image_urls": images,
                "manual_url": manual,
                "product_url": product_url
            })

            print(f"[SUCCESS] Data extracted for model: {model_id or model}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    save_data_to_json(all_data)




lg,

import os
import json
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------- Configuration -------------------- #
config_lg = {
    "model_id": "span.MuiTypography-root.MuiTypography-overline.css-rrulv7",
    "title": "h2.MuiTypography-root.MuiTypography-h5.css-72m7wz",
    "breadcrumb": "ol.MuiBreadcrumbs-ol > li",
    "images": "img",
    "icon_features": "ul.css-1he9hsx li",
    "detailed_features": "div.css-1qtv6i2 li",
}

# -------------------- Playwright Search -------------------- #
def run_playwright_search(model_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://www.lg.com/us", timeout=30000)
            page.wait_for_load_state("load")
            print("✅ LG homepage loaded.")

            page.click('button[aria-label="Search"]')
            page.fill('input[placeholder="Search LG"]', model_id)
            page.press('input[placeholder="Search LG"]', 'Enter')

            page.wait_for_selector('a.css-11xg6yi', timeout=10000)
            first_product = page.locator('a.css-11xg6yi').first
            product_url = first_product.get_attribute("href")

            if product_url:
                full_url = urljoin("https://www.lg.com/us", product_url)
                print(f"✅ First product found: {full_url}")
                return full_url
            else:
                print("❌ No product URL found.")
                return None
        except PlaywrightTimeoutError as e:
            print("❌ Playwright timeout error:", e)
            return None
        except Exception as e:
            print("❌ Playwright search error:", e)
            return None
        finally:
            browser.close()

# -------------------- Selenium Setup -------------------- #
def get_selenium_driver(download_path=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    if download_path:
        prefs = {
            "download.default_directory": os.path.abspath(download_path),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# -------------------- Fetch HTML -------------------- #
def fetch_page_data(driver, product_url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(product_url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config_lg["breadcrumb"]))
            )
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return driver.page_source
        except Exception as e:
            print(f"[ERROR] Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return None

# -------------------- Extract Product Data -------------------- #
def extract_product_data(html, config):
    soup = BeautifulSoup(html, "html.parser")

    def select(selector, attr=None, multi=False):
        elems = soup.select(selector)
        if not elems:
            return [] if multi else ""
        if multi:
            results = []
            for el in elems:
                val = el.get(attr).strip() if attr else el.get_text(strip=True)
                results.append(val)
            return results
        el = elems[0]
        return el.get(attr).strip() if attr else el.get_text(strip=True)

    model_id = select(config["model_id"])
    title = select(config["title"])
    category = "  ".join([el.get_text(strip=True) for el in soup.select(config["breadcrumb"])])

    raw_images = select(config["images"], attr="src", multi=True)
    image_urls = []
    for url in raw_images:
        if not url or url.startswith("data:"):
            continue
        image_urls.append(urljoin("https://www.lg.com/us", url))
    image_urls = list(set(image_urls))

    icon_feat = select(config["icon_features"], multi=True)
    detailed_feat = select(config["detailed_features"], multi=True)
    features = list(dict.fromkeys(icon_feat + detailed_feat))

    return model_id, title, features, image_urls, category

# -------------------- Save to JSON -------------------- #
def save_data_to_json(product_data, filename="lg_data.json"):
    all_data = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                pass
    all_data.append(product_data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
    print(f"✅ Product data saved to {filename}")

# -------------------- Main -------------------- #
if __name__ == "__main__":
    driver = get_selenium_driver()
    try:
        model_id_input = input("Enter LG model ID (e.g., OLED55C2PUA): ").strip()
        if not model_id_input:
            print("❌ Please enter a valid model ID.")
            exit(1)

        product_url = run_playwright_search(model_id_input)
        if not product_url:
            print("❌ Product not found via search.")
            exit(1)

        html = fetch_page_data(driver, product_url)
        if not html:
            print("❌ Failed to load product page.")
            exit(1)

        model_id, title, features, image_urls, category = extract_product_data(html, config_lg)

        product_data = {
            "manufacturer": "LG",
            "model_id": model_id,
            "title": title,
            "category": category,
            "features": features,
            "images": image_urls,
            "product_url": product_url,
        }

        save_data_to_json(product_data)

    finally:
        driver.quit()


whrilpool,
import os
import json
import time
import re
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# -------------------- Configuration -------------------- #
config_whirlpool = {
    "model_id": "span.pdp-tray-model-code",
    "title": "span.product-title",
    "breadcrumb": "ul.breadcrumbs li span[itemprop='name']",
    "key_features": "div.pdp-tray-key-features-list",
    "manual_link": "a[href$='.pdf']",
    "images": "img.product-image",
}

# -------------------- Playwright Search -------------------- #
def run_playwright_search(model_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://www.whirlpool.com/", timeout=60000)
        print("✅ Whirlpool homepage loaded.")
        
        # Try closing modals/popups if present
        modal_selectors = [
            ".conversion-drawer-tab__open-close",
            ".lead-gen-modal__content .close",
            "//button[@aria-label='Close']",
            ".modal-close-button",
        ]
        for selector in modal_selectors:
            try:
                if selector.startswith("//"):
                    close_btn = page.locator(f"xpath={selector}").first
                else:
                    close_btn = page.locator(selector).first
                if close_btn and close_btn.is_visible():
                    close_btn.click()
                    print(f"✅ Closed modal: {selector}")
                    time.sleep(1)
            except Exception:
                # Ignore errors here
                pass
        
        # Perform search
        search_input = page.locator('input.header-search-input[aria-label="Search"]').first
        search_input.wait_for(state="visible", timeout=15000)
        search_input.fill(model_id)
        search_input.press("Enter")
        print(f"✅ Search performed for model ID: {model_id}")
        
        # Wait for search results page to load
        page.wait_for_load_state("load", timeout=60000)

        product_link_locator = page.locator('a.plp-item-detail-link').first
        if product_link_locator.count() == 0:
            print("[ERROR] No product links found.")
            browser.close()
            return None
        
        product_url_suffix = product_link_locator.get_attribute("href")
        if not product_url_suffix:
            print("[ERROR] Product link href is empty.")
            browser.close()
            return None
        
        base_url = "https://www.whirlpool.com"
        product_url = urljoin(base_url, product_url_suffix)
        print(f"✅ Found product URL: {product_url}")
        
        browser.close()
        return product_url

# -------------------- Selenium Setup -------------------- #
def get_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# -------------------- Scraping Functions -------------------- #
def fetch_page_data(driver, url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config_whirlpool["breadcrumb"]))
            )
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print(f"✅ Page loaded: {url}")
            return driver.page_source
        except Exception as e:
            print(f"[ERROR] Attempt {attempt+1} to load page failed: {e}")
            time.sleep(3)
    return None

def extract_background_image_url(style_attr):
    if not style_attr:
        return None
    match = re.search(r'url\(["\']?(.*?)["\']?\)', style_attr)
    if match:
        return match.group(1)
    return None

def extract_product_data(html, config, base_url):
    soup = BeautifulSoup(html, "html.parser")

    def select_data(selector, attr=None, multiple=False):
        elements = soup.select(selector)
        if not elements:
            return [] if multiple else ""
        if multiple:
            result = []
            for el in elements:
                if attr and el.has_attr(attr):
                    result.append(urljoin(base_url, el[attr]))
                else:
                    result.append(el.get_text(strip=True))
            return result
        el = elements[0]
        if attr and el.has_attr(attr):
            return urljoin(base_url, el[attr])
        return el.get_text(strip=True)

    model_id = select_data(config["model_id"])
    title = select_data(config["title"])
    category_items = soup.select(config["breadcrumb"])
    category = " > ".join(item.get_text(strip=True) for item in category_items if item)

    # Get manual PDFs, prefer those containing "manual" keyword
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(base_url, href)
            pdf_links.append(full_url)
    manual_url = next((link for link in pdf_links if "manual" in link.lower()), (pdf_links[0] if pdf_links else ""))

    # Get image URLs from <img> tags
    image_urls = list(set(select_data(config["images"], attr="src", multiple=True)))

    # Optionally, also get background images from inline styles (like div.s7thumb)
    bg_divs = soup.select("div.s7thumb")
    for div in bg_divs:
        style = div.get("style", "")
        bg_url = extract_background_image_url(style)
        if bg_url and bg_url not in image_urls:
            image_urls.append(urljoin(base_url, bg_url))

    key_features_div = soup.select_one(config["key_features"])
    key_features = []
    if key_features_div:
        # Try to find <li> inside, if any
        li_items = key_features_div.find_all("li")
        if li_items:
            key_features = [li.get_text(strip=True) for li in li_items if li.get_text(strip=True)]
        else:
            # fallback: split by bullet if no <li>
            raw_text = key_features_div.get_text(separator="|", strip=True)
            key_features = [feat.strip() for feat in raw_text.split("|") if feat.strip()]

    # Remove bullet chars (•) from the features list
    cleaned_features = [f for f in key_features if f != "•"]

    return model_id, title, cleaned_features, image_urls, manual_url, category


def save_data_to_json(data, filename="whrilpool.json"):
    all_data = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                pass
    all_data.append(data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
    print(f"[SUCCESS] Data saved to {filename}")

# -------------------- Main -------------------- #
if __name__ == "__main__":
    driver = get_selenium_driver()
    try:
        model_id_input = input("Enter Whirlpool model ID (e.g., WFE505W0JZ): ").strip()
        product_url = run_playwright_search(model_id_input)
        if not product_url:
            print("[ERROR] Product not found.")
            exit(1)

        html_content = fetch_page_data(driver, product_url)
        if not html_content:
            print("[ERROR] Failed to load product page.")
            exit(1)

        model_id, title, key_features, image_urls, manual_url, category = extract_product_data(
            html_content, config_whirlpool, product_url
        )

        product_data = {
            "manufacturer": "whirlpool",
            "model_id": model_id,
            "title": title,
            "category": category,
            "key_features": key_features,
            "image_urls": image_urls,
            "manual_url": manual_url,
            "product_url": product_url
        }

        save_data_to_json(product_data)

    finally:
        driver.quit()


