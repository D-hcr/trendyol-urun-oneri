import requests
from bs4 import BeautifulSoup
import time
from sqlalchemy.orm import sessionmaker
from database import engine
from models import ProductInfo

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

category_url = "https://www.trendyol.com/sr?q=güneş+kremi"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(category_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

product_links = []
for a in soup.select("div.p-card-chldrn-cntnr a"):
    link = "https://www.trendyol.com" + a.get("href")
    product_links.append(link)

print(f"{len(product_links)} ürün bulundu.")

for product_url in product_links[:5]:
    print(f"İşleniyor: {product_url}")
    product_response = requests.get(product_url, headers=headers)
    product_soup = BeautifulSoup(product_response.text, "html.parser")

    title = product_soup.select_one("h1")
    title = title.text.strip() if title else "Bilinmiyor"

    price = product_soup.select_one(".price-item")
    price = price.text.strip().replace("₺", "").replace(",", ".") if price else "0.0"

    # **Özellikleri varsayılan olarak None olarak belirle**
    attributes = {
        "SPF": None,
        "Cilt Tipi": None,
        "Görünüm": None,
        "Ek Özellik": None,
        "Hacim": None,
        "Kullanma Amacı": None,
        "Form": None,
        "Tip": None,
        "Yaşlanma Karşıtı": None,
        "Menşei": None
    }

    for attr in product_soup.select("li.detail-attr-item"):
        key_element = attr.select_one(".attr-name")
        value_element = attr.select_one(".attr-value-name-w")

        if key_element and value_element:
            key = key_element.text.strip()
            value = value_element.text.strip()
            attributes[key] = value  # Eğer özellik varsa ekle, yoksa None kalır.

    product = ProductInfo(
        product_name=title,
        price=float(price),
        spf=attributes["SPF"],
        skin_type=attributes["Cilt Tipi"],
        appearance=attributes["Görünüm"],
        extra_features=attributes["Ek Özellik"],
        volume=attributes["Hacim"],
        usage=attributes["Kullanma Amacı"],
        form=attributes["Form"],
        type=attributes["Tip"],
        anti_aging=attributes["Yaşlanma Karşıtı"],
        origin=attributes["Menşei"]
    )

    session.add(product)
    session.commit()
    print(f"{title} kaydedildi!")
    time.sleep(1)

session.close()
print("Tüm ürünler başarıyla kaydedildi!")
