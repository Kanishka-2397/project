import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Setup download directory
download_dir = r"C:\Users\sarav\Downloads\selenium\download_dir"
os.makedirs(download_dir, exist_ok=True)

# ✅ Chrome options
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})

# ✅ Start browser
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.maximize_window()

# ✅ Start from product page
product_url = "https://www.lg.com/us/wireless-headphones/lg-t90S-black-tone-free-earbuds"
print(f"\n🌐 Visiting product page: {product_url}")
driver.get(product_url)
time.sleep(3)

# ✅ Click the 'Support' link to go to support page
try:
    support_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/support/product/')]"))
    )
    support_link = support_button.get_attribute("href")
    print(f"➡️ Found support link: {support_link}")
    driver.get(support_link)
    time.sleep(3)
except Exception as e:
    print("❌ Could not find support link:", e)
    driver.quit()
    exit()

# ✅ Download manuals and PDFs
try:
    # Click "Manuals & Software" tab
    manual_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Manuals & Software')]"))
    )
    manual_tab.click()
    print("📖 Clicked 'Manuals & Software' tab")
    time.sleep(3)

    # Find all download icons
    svg_icons = driver.find_elements(By.XPATH, "//svg[@data-testid='DocumentScannerOutlinedIcon']")
    img_icons = driver.find_elements(By.XPATH, "//img[@alt='download']")
    download_icons = svg_icons if svg_icons else img_icons

    print(f"🖱️ Found {len(download_icons)} download icon(s)")
    for idx, icon in enumerate(download_icons):
        try:
            parent_btn = icon.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiBox-root')][1]")
            driver.execute_script("arguments[0].click();", parent_btn)
            print(f"⬇️ Clicked download button {idx + 1}")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Failed to click download button {idx + 1}: {e}")
except Exception as e:
    print("❌ Error while downloading:", e)

# ✅ Close browser
driver.quit()

# ✅ Wait for downloads to finish
def wait_for_downloads(dir_path, timeout=60):
    print("\n⏳ Waiting for downloads to finish...")
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
