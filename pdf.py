# scraper.py
import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tools import get_config

# -------------------- Setup -------------------- #
config = get_config()
URLS = config["url"]
BASE_FOLDER = "download"
os.makedirs(BASE_FOLDER, exist_ok=True)

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)

# -------------------- Functions -------------------- #
def fetch_page_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = session.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def extract_product_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    config_items = config['item']

    def select_text(selector, multiple=False):
        if multiple:
            return [tag.get_text(strip=True) for tag in soup.select(selector) if tag.get_text(strip=True)]
        tag = soup.select_one(selector)
        return tag.get_text(strip=True) 
    

    model_id = select_text(config_items[0]['selector'])
    title = select_text(config_items[1]['selector'])
    key_features = select_text(config_items[2]['selector'], multiple=True)
    image_urls = list({img.get("src") for img in soup.select(config_items[3]['selector']) if img.get("src")})

    return model_id, title, key_features, image_urls

def download_images(image_urls, folder, base_url):
    os.makedirs(folder, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    for idx, url in enumerate(image_urls):
        full_url = urljoin(base_url, url)
        img_data = session.get(full_url, headers=headers).content
        with open(os.path.join(folder, f"image_{idx+1}.jpg"), "wb") as f:
            f.write(img_data)

def get_chrome_driver(headless=True, download_path=None):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
    if download_path:
        options.add_experimental_option('prefs', {
            "download.default_directory": os.path.abspath(download_path),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        })
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def wait_for_downloads(dir_path, timeout=60):
    for _ in range(timeout):
        if any(f.endswith(".crdownload") for f in os.listdir(dir_path)):
            time.sleep(1)
        else:
            break

def download_manuals_with_pdf(product_url, download_folder):
    os.makedirs(download_folder, exist_ok=True)
    driver = get_chrome_driver(headless=False, download_path=download_folder)
    driver.get(product_url)
    time.sleep(3)


    support_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/support/product/')]"))
    )
    driver.get(support_button.get_attribute("href"))
    time.sleep(3)

    manual_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Manuals & Software')]"))
    )
    manual_tab.click()
    time.sleep(3)

    icons = driver.find_elements(By.XPATH, "//svg[@data-testid='DocumentScannerOutlinedIcon']") or \
            driver.find_elements(By.XPATH, "//img[@alt='download']")

    for icon in icons:
        btn = icon.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiBox-root')][1]")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)

    driver.quit()
    wait_for_downloads(download_folder)

def save_data_to_json(product_data):
    json_path = os.path.join(BASE_FOLDER, "data.json")
    all_data = []

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)

    all_data.append(product_data)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

# -------------------- Run -------------------- #
if __name__ == "__main__":
    for url in URLS:
        html = fetch_page_data(url)


        model_id, title, key_features, image_urls = extract_product_data(html)
        product_folder = os.path.join(BASE_FOLDER, model_id)
        images_folder = os.path.join(product_folder, "images")
        manuals_folder = os.path.join(product_folder, "manuals")

        download_images(image_urls, images_folder, url)
        download_manuals_with_pdf(url, manuals_folder)

        save_data_to_json({
            "model_id": model_id,
            "title": title,
            "key_features": key_features,
            "image_urls": image_urls,
            "product_url": url
        })

  
