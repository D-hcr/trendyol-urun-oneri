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

    attributes = {}
    for attr in product_soup.select("li.detail-attr-item"):
        key = attr.select_one(".attr-name").text.strip()
        value = attr.select_one(".attr-value-name-w").text.strip()
        attributes[key] = value

    product = ProductInfo(
        product_name=title,
        price=float(price),
        spf=attributes.get("SPF"),
        skin_type=attributes.get("Cilt Tipi"),
        appearance=attributes.get("Görünüm"),
        type=attributes.get("Ürün Tipi"),
        extra_features=attributes.get("Ek Özellikler"),
        volume=attributes.get("Hacim"),
        usage=attributes.get("Kullanım"),
        form=attributes.get("Form")
    )

    session.add(product)
    session.commit()
    print(f"{title} kaydedildi!")
    time.sleep(1)

session.close()
print("Tüm ürünler başarıyla kaydedildi!")
