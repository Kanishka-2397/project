import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Setup download directory
download_dir = r"C:\Users\sarav\Downloads\selenium"
os.makedirs(download_dir, exist_ok=True)

# ✅ Setup Chrome options
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})

# ✅ Start browser
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get("https://www.lg.com/us/support/product/lg-TONE-T80S.AUSALBK")
driver.maximize_window()

try:
    # Click 'Manuals & Software' tab
    manual_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Manuals & Software')]"))
    )
    manual_tab.click()
    print("📖 Clicked 'Manuals & Software' tab")

    time.sleep(3)  # Allow download icons to appear

    # Click all visible download icons (based on download arrow image alt)
    download_icons = driver.find_elements(By.XPATH, "//img[@alt='download']")
    print(f"🖱️ Found {len(download_icons)} download icon(s)")

    for idx, icon in enumerate(download_icons):
        try:
            parent_btn = icon.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiBox-root')][1]")
            driver.execute_script("arguments[0].click();", parent_btn)
            print(f"⬇️ Clicked download button {idx + 1}")
            time.sleep(3)  # Give time for the download to start
        except Exception as e:
            print(f"⚠️ Failed to click download button {idx + 1}: {e}")

except Exception as e:
    print("❌ Failed to access download area:", e)

driver.quit()

# ✅ Wait for files to complete download (look for .crdownload temp files)
def wait_for_downloads(dir_path, timeout=30):
    print("⏳ Waiting for downloads to finish...")
    for _ in range(timeout):
        if any(f.endswith(".crdownload") for f in os.listdir(dir_path)):
            time.sleep(1)
        else:
            break

wait_for_downloads(download_dir)

# ✅ List downloaded files
print("\n📂 Downloaded PDF files:")
for file in os.listdir(download_dir):
    if file.endswith(".pdf"):
        print(f"- {file}")







# 2 type

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup download directory
download_dir = r"C:\Users\sarav\Downloads\selenium\download_dir"
os.makedirs(download_dir, exist_ok=True)

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})

# List of product/support URLs
product_urls = [
    "https://www.lg.com/us/wireless-headphones/lg-t90S-black-tone-free-earbuds",
    "https://www.lg.com/us/support/product/lg-TONE-T80S.AUSALBK"
]

# Start browser
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.maximize_window()

def download_pdfs_from_page():
    # Click tab if on support page
    try:
        manual_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Manuals & Software')]"))
        )
        manual_tab.click()
        print("Clicked 'Manuals & Software' tab")
        time.sleep(3)
    except:
        pass  # It might not be a support page

    # Scroll to section if on product page
    try:
        manual_section = driver.find_element(By.XPATH, "//h6[contains(text(), 'Manuals and Downloads')]")
        driver.execute_script("arguments[0].scrollIntoView();", manual_section)
        print("Scrolled to 'Manuals and Downloads' section")
        time.sleep(2)
    except:
        pass  # Might not be a product page

    # Try to find and click all download icons (SVG or IMG)
    svg_icons = driver.find_elements(By.XPATH, "//svg[@data-testid='DocumentScannerOutlinedIcon']")
    img_icons = driver.find_elements(By.XPATH, "//img[@alt='download']")
    download_icons = svg_icons if svg_icons else img_icons

    print(f"Found {len(download_icons)} download icon(s)")

    for idx, icon in enumerate(download_icons):
        try:
            parent_btn = icon.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiBox-root')][1]")
            driver.execute_script("arguments[0].click();", parent_btn)
            print(f"Clicked download button {idx + 1}")
            time.sleep(3)
        except Exception as e:
            print(f"Failed to click download button {idx + 1}: {e}")

# Process all URLs
for url in product_urls:
    print(f"\nVisiting: {url}")
    driver.get(url)
    time.sleep(3)
    try:
        download_pdfs_from_page()
    except Exception as e:
        print("Error while processing:", e)

# Close browser
driver.quit()

# Wait for all downloads to complete
def wait_for_downloads(dir_path, timeout=60):
    print("\nWaiting for downloads to finish...")
    for _ in range(timeout):
        if any(f.endswith(".crdownload") for f in os.listdir(dir_path)):
            time.sleep(1)
        else:
            break

wait_for_downloads(download_dir)

# List downloaded PDF files
print("\nDownloaded PDF files:")
for file in os.listdir(download_dir):
    if file.endswith(".pdf"):
        print(f"- {file}")

