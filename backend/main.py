from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from data.database import SessionLocal
from data.models import ProductInfo

app = FastAPI()

# CORS ayarları – frontend ile bağlantı için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme sırasında tüm kaynaklara izin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı bağlantısını dependency olarak ayarla
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model – gelen mesaj için
class Message(BaseModel):
    message: str

# Ana endpoint – frontend'ten gelen istekleri işler
@app.post("/chat")
def chat(msg: Message, db: Session = Depends(get_db)):
    user_query = msg.message.lower()

    if "kuru" in user_query:
        product = db.query(ProductInfo).filter(ProductInfo.skin_type.ilike("%kuru%")).first()
    else:
        product = db.query(ProductInfo).first()

    if product:
        return {
            "reply": (
                f"✅ Ürün Önerisi:\n"
                f"🧴 {product.product_name}\n"
                f"💰 Fiyat: {product.price} TL\n"
                f"☀️ SPF: {product.spf}\n"
                f"👤 Cilt Tipi: {product.skin_type}\n"
                f"🔗 Ürün Linki: {product.product_url}"
            )
        }
    else:
        return {"reply": "❌ Uygun ürün bulunamadı."}
