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
