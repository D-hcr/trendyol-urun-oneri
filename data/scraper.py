import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def get_product_links(category_url, max_products=200, max_scrolls=10):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Arka planda çalıştırmak için, eğer sorun yaşarsan kaldır.
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(category_url)
        time.sleep(5)

        product_links = set()  # Aynı ürünleri eklememek için set kullanıyoruz
        scroll_count = 0  

        while len(product_links) < max_products and scroll_count < max_scrolls:
            products = driver.find_elements(By.CSS_SELECTOR, "div.p-card-chldrn-cntnr a")
            
            for product in products:
                link = product.get_attribute("href")
                if link and link.startswith("https://www.trendyol.com"):
                    product_links.add(link)
                    if len(product_links) >= max_products:
                        break  

            # Sayfayı aşağı kaydır
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Sayfanın yüklenmesi için bekleme süresi
            scroll_count += 1  

    except Exception as e:
        print("Hata oluştu (get_product_links):", e)
        print(traceback.format_exc())

    finally:
        driver.quit()

    return list(product_links)

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Eğer sorun yaşarsan kaldır
    driver = webdriver.Chrome(options=options)
    return driver

def get_product_details(product_url):
    driver = setup_driver()
    
    try:
        driver.get(product_url)

        product_name = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.pr-new-br"))
        ).text

        price_element = driver.find_elements(By.CSS_SELECTOR, "span.prc-dsc")
        if price_element:
            price_text = price_element[0].text.replace(" TL", "").replace(".", "").replace(",", ".").strip()
            price = float(price_text) if price_text else None
        else:
            price = None


        # Varsayılan değerler
        spf = skin_type = appearance = extra_features = volume = usage = form = type = anti_aging = origin = "null"

        # Ürün özelliklerini alma
        features = driver.find_elements(By.CSS_SELECTOR, "li.detail-attr-item")
        for feature in features:
            try:
                key_element = feature.find_element(By.CSS_SELECTOR, "span.attr-name")
                value_element = feature.find_element(By.CSS_SELECTOR, "span[title]")
                
                if key_element and value_element:
                    key = key_element.text.strip()
                    value = value_element.get_attribute("title").strip()
                    
                    if "SPF" in key:
                        spf = value
                    elif "Cilt Tipi" in key:
                        skin_type = value
                    elif "Görünüm" in key:
                        appearance = value
                    elif "Ek Özellik" in key:
                        extra_features = value
                    elif "Hacim" in key:
                        volume = value
                    elif "Kullanma Amacı" in key:
                        usage = value
                    elif "Form" in key:
                        form = value
                    elif "Tip" in key:
                        type = value
                    elif "Yaşlanma Karşıtı" in key:
                        anti_aging = value
                    elif "Menşei" in key:
                        origin = value
            except:
                continue
        
        return {
            "name": product_name,
            "price": price,
            "spf": spf,
            "skin_type": skin_type,
            "appearance": appearance,
            "extra_features": extra_features,
            "volume": volume,
            "usage": usage,
            "form": form,
            "type": type,
            "anti_aging": anti_aging,
            "origin": origin,
            "url": product_url
        }

    except Exception as e:
        print("Hata oluştu (get_product_details):", e)
        print(traceback.format_exc())
        return None

    finally:
        driver.quit()  # Driver'ı her durumda kapat

# Örnek kullanım:
if __name__ == "__main__":
    category_url = "https://www.trendyol.com/..."  # Kendi kategori URL'ni ekle
    product_links = get_product_links(category_url, max_products=10)
    
    print(f"Toplam {len(product_links)} ürün bulundu.")
    
    for link in product_links[:2]:  # İlk 2 ürünü al
        product_data = get_product_details(link)
        if product_data:
            print("✅ Ürün başarıyla alındı:", product_data)
        else:
            print("⛔ Ürün bilgisi alınamadı.")
