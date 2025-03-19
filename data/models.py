from sqlalchemy import Column, Integer, String, Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from database import engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ProductInfo(Base):
    __tablename__ = "product_info"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    product_url = Column(String, nullable=False)
    spf = Column(String, nullable=True)
    skin_type = Column(String, nullable=True)
    appearance = Column(String, nullable=True)
    extra_features = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    usage = Column(String, nullable=True)
    form = Column(String, nullable=True)
    type = Column(String, nullable=True)
    anti_aging = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    reviews_url = Column(String, nullable=True)

    reviews = relationship("Review", back_populates="product")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product_info.id"), nullable=False)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    review_date = Column(TIMESTAMP, nullable=False)

    product = relationship("ProductInfo", back_populates="reviews")

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)
