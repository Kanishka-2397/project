from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
    "download.default_directory": r"C:\Users\sarav\Downloads\s3",
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
URL = 'https://www.lg.com/us/support/product/lg-LRFLC2706S.ASTCNA0'
driver.get(URL)

driver.maximize_window()
driver.implicitly_wait(10)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)


pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")

count = 0
for link in pdf_links:
    link_text = link.text.lower()
    href = link.get_attribute("href")

    if "Articles" in link_text or "guide" in link_text:
        print(f"Downloading: {href}")
        link.click()
        time.sleep(2)  
        count += 1

    if count >= 10:
        break

driver.quit()


