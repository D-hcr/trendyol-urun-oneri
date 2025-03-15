from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_product_links(category_url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(category_url)
    time.sleep(5)

    product_links = []
    products = driver.find_elements(By.CSS_SELECTOR, "div.p-card-chldrn-cntnr a")
    
    for product in products:
        link = product.get_attribute("href")
        if link and link.startswith("https://www.trendyol.com"):
            product_links.append(link)

    driver.quit()
    
    return product_links

def get_product_details(product_url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(product_url)
    time.sleep(3)

    try:
        product_name = driver.find_element(By.CSS_SELECTOR, "h1.pr-new-br").text
        price = driver.find_element(By.CSS_SELECTOR, "span.prc-dsc").text.replace(" TL", "").replace(",", ".")
        price = float(price) if price else 0

        spf = skin_type = appearance = extra_features = ""

        try:
            features = driver.find_elements(By.CSS_SELECTOR, "li.detail-attr-item")
            for feature in features:
                text = feature.text
                if "SPF" in text:
                    spf = text.split(":")[-1].strip()
                elif "Cilt Tipi" in text:
                    skin_type = text.split(":")[-1].strip()
                elif "Görünüm" in text:
                    appearance = text.split(":")[-1].strip()
                elif "Ekstra Özellikler" in text:
                    extra_features = text.split(":")[-1].strip()
        
        except:
            pass

        driver.quit()

        return {
            "name": product_name,
            "price": price,
            "url": product_url,
            "spf": spf,
            "skin_type": skin_type,
            "appearance": appearance,
            "extra_features": extra_features
        }

    except Exception as e:
        driver.quit()
        print(f"Hata: {e}")
        return None