from sqlalchemy.orm import Session
from database import SessionLocal
from models import ProductInfo
from scraper import get_product_links, get_product_details

def save_product_to_db(details, added_products):
    db: Session = SessionLocal()

    # Ürün zaten eklenmişse ekleme
    existing_product = db.query(ProductInfo).filter_by(product_url=details["url"]).first()
    if existing_product or details["url"] in added_products:
        db.close()
        return False

    product = ProductInfo(
        product_name=details["name"],
        price=details["price"],
        product_url=details["url"],
        spf=details["spf"],
        skin_type=details["skin_type"],
        appearance=details["appearance"],
        extra_features=details["extra_features"]
    )

    db.add(product)
    db.commit()
    db.close()
    
    added_products.add(details["url"])
    return True

if __name__ == "__main__":
    category_url = "https://www.trendyol.com/sr?q=güneş+kremi"
    product_links = get_product_links(category_url)

    print(f"🔎 {len(product_links)} ürün bulundu. İlk 2 ürün kaydedilecek...")

    added_products = set()
    saved_count = 0

    for link in product_links:
        if saved_count >= 2:  # İlk 2 üründen sonra dur
            break

        details = get_product_details(link)
        if details and save_product_to_db(details, added_products):
            saved_count += 1
    
    print("İlk 2 ürün başarıyla kaydedildi!")
