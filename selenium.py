from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup #parsing HTML and extracting data
from urllib.parse import urljoin, urlparse # clean/join URLs
import time #pause execution where needed

DOWNLOAD_FOLDER = "downloaded_data"  # folder name set
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # folder create

def download_file(url, filename): # fun call
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  #network API request
        response = requests.get(url, stream=True, timeout=10, headers=headers) # variable store
        if response.status_code == 200: #request check
            with open(filename, 'wb') as f: 
                # chunk-- used to stream the safely and efficiently
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def get_support_pdf_links(model_id):
    support_url = f"https://www.lg.com/us/support/product/{model_id}"
    print(f"Fetching support PDFs from: {support_url}")
    options = Options() # chrome option
    options.add_argument("--headless") # run without a visible windows
    options.add_argument("--disable-gpu")  # disbles GPU hardware acceleration
    options.add_argument("--no-sandbox")  # security sandbox 
    driver = webdriver.Chrome(service=Service(), options=options)

    pdf_links = []
    # scripted web scraping, low resource env, ci pipelines or docker containers

    try:
        driver.get(support_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".pdf" in href:
                full_pdf_url = urljoin(support_url, href)
                if full_pdf_url not in pdf_links:
                    pdf_links.append(full_pdf_url)

    except Exception as e:
        print(f"Error scraping support page: {e}")
    finally:
        driver.quit()

    return pdf_links

def get_data_from_product_page(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        path = urlparse(url).path # path part url
        model_id = path.strip("/").split("/")[-1].split(".")[0].lower() # convert everything to lowercase
        #strip-- remove any leading/trailing slashes
        #split-- take last part of the path
        images = set()
        for img in soup.find_all("img"):
            src = (
                img.get("src")
                or img.get("data-src")  # lazy-loaded img or responsive designs
                or img.get("data-original")
                or img.get("data-lazy")
                or img.get("data-srcset")
            )
            if src:
                img_url = urljoin(url, src.split()[0])
                if img_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    images.add(img_url)

        key_features = []
        sections = soup.select(".key-feature, .feature-section, .keyFeatures, .product-highlights, .product-feature-item")
        for section in sections:
            text = section.get_text(separator=" ", strip=True)
            if text:
                key_features.append(text)

        if not key_features:
            for item in soup.select("ul li"):
                text = item.get_text(strip=True)
                if text:
                    key_features.append(text)

        return {
            "model_id": model_id,
            "images": list(images)[:3],
            "key_features": key_features[:10]
        }

    finally:
        driver.quit()

# URLs to process
product_urls = [
    "https://www.lg.com/us/refrigerators/lg-lrflc2706s-french-3-door-refrigerator",
    "https://www.lg.com/us/refrigerators/lg-lrsos2706d-side-by-side-refrigerator",
]

# Output files
img_url_file = os.path.join(DOWNLOAD_FOLDER, "image_urls.txt")
features_file = os.path.join(DOWNLOAD_FOLDER, "key_features.txt")

open(img_url_file, "w", encoding="utf-8").close()
open(features_file, "w", encoding="utf-8").close()

# Main loop
for idx, url in enumerate(product_urls, 1):
    # enumerate-- loops to automatically add a counter(index)
    print(f"\n[{idx}] Processing product: {url}")
    try:
        data = get_data_from_product_page(url)
        model_id = data["model_id"]

        # Save image URLs and download images
        with open(img_url_file, "a", encoding="utf-8") as img_out:
            for i, img_url in enumerate(data["images"]):
                img_out.write(f"{model_id}: {img_url}\n")
                ext = os.path.splitext(img_url)[-1].split("?")[0]
                if not ext or len(ext) > 5:
                    ext = ".jpg"
                img_file = os.path.join(DOWNLOAD_FOLDER, f"{model_id}_img_{i+1}{ext}")
                download_file(img_url, img_file)

        # Save key features
        with open(features_file, "a", encoding="utf-8") as feat_out:
            feat_out.write(f"{model_id}:\n")
            for feat in data["key_features"]:
                feat_out.write(f" - {feat}\n")
            feat_out.write("\n")

        # Download support page PDFs
        pdf_links = get_support_pdf_links(model_id)
        for i, pdf_url in enumerate(pdf_links):
            pdf_file = os.path.join(DOWNLOAD_FOLDER, f"{model_id}_pdf_{i+1}.pdf")
            download_file(pdf_url, pdf_file)

    except Exception as e:
        print(f"Error: {e}")




##2type 


import os
import time
import json
import shutil
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create necessary folders
DOWNLOAD_FOLDER = "downloaded_data"
MANUALS_FOLDER = os.path.join(DOWNLOAD_FOLDER, "manuals")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(MANUALS_FOLDER, exist_ok=True)

# Setup retry logic for requests
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Chrome driver helper
def get_chrome_driver(headless=True, download_path=None):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0")
    if download_path:
        options.add_experimental_option('prefs', {
            "download.default_directory": os.path.abspath(download_path),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        })
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Download file using requests
def download_file(url, filename):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = session.get(url, stream=True, timeout=10, headers=headers)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Wait until .crdownload files are finished
def wait_for_downloads(dir_path, timeout=60):
    print("Waiting for PDF downloads to finish...")
    for _ in range(timeout):
        if any(f.endswith(".crdownload") for f in os.listdir(dir_path)):
            time.sleep(1)
        else:
            break

# Extract product data
def extract_product_data(url):
    driver = get_chrome_driver(headless=True)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        path = urlparse(url).path
        model_id = path.strip("/").split("/")[-1].split(".")[0].lower()

        images = set()
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("data-srcset")
            if src:
                img_url = urljoin(url, src.split()[0])
                if img_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    images.add(img_url)

        key_features = []
        sections = soup.select(".key-feature, .feature-section, .keyFeatures, .product-highlights, .product-feature-item")
        for section in sections:
            text = section.get_text(separator=" ", strip=True)
            if text:
                key_features.append(text)

        if not key_features:
            for item in soup.select("ul li"):
                text = item.get_text(strip=True)
                if text:
                    key_features.append(text)

        return {
            "model_id": model_id,
            "images": list(images)[:3],
            "key_features": key_features[:10]
        }
    finally:
        driver.quit()

# Manual PDF download using UI automation
def download_manuals_with_ui(product_url, model_id):
    driver = get_chrome_driver(headless=True, download_path=MANUALS_FOLDER)
    driver.maximize_window()

    try:
        driver.get(product_url)
        time.sleep(3)

        support_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/support/product/')]"))
        )
        support_link = support_button.get_attribute("href")
        print(f"Navigating to support page: {support_link}")
        driver.get(support_link)
        time.sleep(3)

        manual_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Manuals & Software')]"))
        )
        manual_tab.click()
        print("Opened 'Manuals & Software' tab")
        time.sleep(3)

        icons = driver.find_elements(By.XPATH, "//svg[@data-testid='DocumentScannerOutlinedIcon']") or \
                driver.find_elements(By.XPATH, "//img[@alt='download']")

        for idx, icon in enumerate(icons):
            try:
                parent_btn = icon.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiBox-root')][1]")
                driver.execute_script("arguments[0].click();", parent_btn)
                print(f"Downloaded manual {idx + 1}")
                time.sleep(2)
            except Exception as e:
                print(f"Could not click manual {idx + 1}: {e}")

    except Exception as e:
        print(f"Error during manual download: {e}")
    finally:
        driver.quit()

    wait_for_downloads(MANUALS_FOLDER)

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LG Product Scraper")
    parser.add_argument("url", help="LG product page URL")
    parser.add_argument("--no-manual", action="store_true", help="Skip manual PDF download")
    parser.add_argument("--only-images", action="store_true", help="Download only images")
    args = parser.parse_args()

    product_url = args.url
    print(f"Processing product URL: {product_url}")

    try:
        data = extract_product_data(product_url)
        model_id = data["model_id"]

        for i, img_url in enumerate(data["images"]):
            ext = os.path.splitext(img_url)[-1].split("?")[0]
            if not ext or len(ext) > 9:
                ext = ".jpg"
            img_file = os.path.join(DOWNLOAD_FOLDER, f"{model_id}_img_{i+1}{ext}")
            download_file(img_url, img_file)

        if not args.only_images:
            features_path = os.path.join(DOWNLOAD_FOLDER, f"{model_id}_features.txt")
            with open(features_path, "w", encoding="utf-8") as f:
                for feat in data["key_features"]:
                    f.write(f"- {feat}\n")

            metadata = {
                "model_id": model_id,
                "product_url": product_url,
                "image_urls": data["images"],
                "key_features": data["key_features"]
            }
            json_path = os.path.join(DOWNLOAD_FOLDER, f"{model_id}_metadata.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
            print(f"Metadata saved to: {json_path}")

        if not args.no_manual:
            download_manuals_with_ui(product_url, model_id)

        zip_path = shutil.make_archive(f"{model_id}_bundle", 'zip', DOWNLOAD_FOLDER)
        print(f"Data zipped to: {zip_path}")

    except Exception as e:
        print(f"Error processing product: {e}")

    print("Product processed successfully.")
    print("Downloaded Manual PDFs:")
    for file in os.listdir(MANUALS_FOLDER):
        if file.endswith(".pdf"):
            print(f"- {file}")

