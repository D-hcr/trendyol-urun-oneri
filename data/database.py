from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:386744@localhost:5432/trendyol_scraper"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

print("Veritabanı bağlantısı başarılı!")

