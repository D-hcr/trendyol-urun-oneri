import re
import time
import locale
import traceback
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def get_product_links(category_url, max_products=200, max_scrolls=50):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(category_url)
        time.sleep(5)

        product_links = set()  
        scroll_count = 0  

        while len(product_links) < max_products and scroll_count < max_scrolls:
            products = driver.find_elements(By.CSS_SELECTOR, "div.p-card-chldrn-cntnr a")
            
            for product in products:
                link = product.get_attribute("href")
                if link and link.startswith("https://www.trendyol.com"):
                    product_links.add(link)
                    if len(product_links) >= max_products:
                        break  

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  
            scroll_count += 1  

    except Exception as e:
        print("Hata oluştu (get_product_links):", e)
        print(traceback.format_exc())

    finally:
        driver.quit()

    return list(product_links)

def setup_driver():
    options = webdriver.ChromeOptions()
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

        try:
            reviews_element = driver.find_element(By.CSS_SELECTOR, "div.rvw-cnt a")
            reviews_url = reviews_element.get_attribute("href") if reviews_element else None
        except:
            reviews_url = None

        spf = skin_type = appearance = extra_features = volume = usage = form = type = anti_aging = origin = "null"

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
            "url": product_url,
            "reviews_url": reviews_url
        }

    except Exception as e:
        print("Hata oluştu (get_product_details):", e)
        print(traceback.format_exc())
        return None

    finally:
        driver.quit()  

try:
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, "tr_TR")
    except locale.Error:
        print("Türkçe tarih formatı ayarlanamadı, varsayılan kullanılacak.")

def extract_width_value(style_string):
    """style içindeki width değerini alır (hem % hem px olarak)."""
    match = re.search(r'width:\s*(\d+)(%|px)', style_string)
    if match:
        width_value = int(match.group(1))
        return width_value
    return 0 

def get_product_reviews(reviews_url, max_reviews=50):
    if not reviews_url:
        return []

    driver = setup_driver()
    reviews = []
    scroll_count = 0  
    max_scrolls = 15  

    try:
        driver.get(reviews_url)
        time.sleep(3)

        while len(reviews) < max_reviews and scroll_count < max_scrolls:
            review_elements = driver.find_elements(By.CSS_SELECTOR, "div.comment")

            for review_element in review_elements:
                if len(reviews) >= max_reviews:
                    break

                try:
                    review_text = review_element.find_element(By.CSS_SELECTOR, "div.comment-text p").text.strip()

                    rating_html = review_element.find_element(By.CSS_SELECTOR, "div.comment-rating").get_attribute("outerHTML")
                    soup = BeautifulSoup(rating_html, "html.parser")

                    full_stars = 0  
                    star_elements = soup.select(".comment-rating .star-w .full")

                    for star in star_elements:
                        style = star.get("style", "")
                        width_value = extract_width_value(style)  

                        if width_value >= 100:
                            full_stars += 1  
                        elif width_value >= 50:
                            full_stars += 1  

                    if full_stars < 1 or full_stars > 5:
                        full_stars = None  

                    date_text = None
                    date_elements = review_element.find_elements(By.CSS_SELECTOR, "div.comment-info-item")
                    
                    for element in date_elements:
                        raw_text = element.text.strip()
                        try:
                            review_date = datetime.strptime(raw_text, "%d %B %Y")
                            date_text = review_date.strftime("%Y-%m-%d")  
                            break  
                        except ValueError:
                            continue  

                    reviews.append({
                        "review_text": review_text,
                        "rating": full_stars,
                        "review_date": date_text
                    })
                except Exception as e:
                    print("Hata oluştu (Tekil yorum çekme):", e)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  
            scroll_count += 1

    except Exception as e:
        print("Hata oluştu (get_product_reviews):", e)

    finally:
        driver.quit()

    return reviews



