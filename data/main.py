from sqlalchemy.orm import Session
from database import SessionLocal
from models import ProductInfo, Review
from scraper import get_product_links, get_product_details, get_product_reviews

def save_product_to_db(details, added_products):
    db: Session = SessionLocal()

    existing_product = db.query(ProductInfo).filter_by(product_url=details["url"]).first()
    if existing_product or details["url"] in added_products:
        db.close()
        return None  

    product = ProductInfo(
        product_name=details["name"],
        price=details["price"],
        product_url=details["url"],
        spf=details["spf"],
        skin_type=details["skin_type"],
        appearance=details["appearance"],
        extra_features=details["extra_features"],
        volume=details["volume"],
        usage=details["usage"],
        form=details["form"],
        type=details["type"],
        anti_aging=details["anti_aging"],
        origin=details["origin"],     
        reviews_url=details["reviews_url"]
    )

    db.add(product)
    db.commit()
    product_id = product.id 
    db.close()
    
    added_products.add(details["url"])
    return product_id  

def save_reviews_to_db(product_id, reviews):
    db: Session = SessionLocal()

    for review in reviews:
        review_entry = Review(
            product_id=product_id, 
            review_text=review["review_text"], 
            rating=review["rating"], 
            review_date=review["review_date"]
        )
        db.add(review_entry)

    db.commit()
    db.close()
    
if __name__ == "__main__":
    category_url = "https://www.trendyol.com/sr?q=güneş+kremi"
    product_links = get_product_links(category_url, max_products=100)  

    print(f"🔎 {len(product_links)} ürün bulundu.")

    added_products = set()

    for link in product_links:
        details = get_product_details(link)
        if details:
            product_id = save_product_to_db(details, added_products)  
            if product_id:
                reviews = get_product_reviews(details["reviews_url"], max_reviews=50)  
                save_reviews_to_db(product_id, reviews)
    
    print("Bşarıyla kaydedildi!")
