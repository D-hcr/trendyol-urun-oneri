import pandas as pd
import re
import joblib
from sqlalchemy import create_engine, text

# DB bağlantısı
DATABASE_URL = "postgresql://postgres:386744@localhost:5432/trendyol_scraper"
engine = create_engine(DATABASE_URL)

# En fazla 50 yorum çek her ürün için
query = """
    SELECT id, product_id, review_text
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY id) as rn
        FROM reviews
    ) t
    WHERE rn <= 50;
"""
df = pd.read_sql(query, engine)

# ---------- ÖN İŞLEME ----------
turkce_stopwords = ["ve", "bir", "bu", "da", "de", "için", "ile", "ama", "gibi", "çok", "daha", "en", "mi", "mı", "mu", "mü"]

def temizle_stopwords(metin, stopword_list):
    kelimeler = metin.split()
    return " ".join([kelime for kelime in kelimeler if kelime not in stopword_list])

def remove_emojis(metin):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', metin)

def temizle(metin):
    if pd.isna(metin):
        return ""
    metin = metin.lower()
    metin = re.sub(r'\d+', '', metin)
    metin = re.sub(r'http[s]?://\S+', '', metin)
    metin = re.sub(r'([!?.])\1+', r'\1', metin)
    return metin

def full_pipeline(metin):
    metin = temizle(metin)
    metin = remove_emojis(metin)
    metin = temizle_stopwords(metin, turkce_stopwords)
    return metin

# Yorumları temizle
df["clean_review"] = df["review_text"].apply(full_pipeline)

# ---------- MODEL YÜKLEME ----------
model = joblib.load("/home/hacer/Desktop/trendyol/for_reviews_model/naive_bayes_model.pkl")
vectorizer = joblib.load("/home/hacer/Desktop/trendyol/for_reviews_model/naive_bayes_vectorizer.pkl")

# Tahminler
X = vectorizer.transform(df["clean_review"])
df["is_positive"] = model.predict(X)  # 0 = olumlu, 1 = olumsuz (senin sistemine göre)

# ---------- YORUMLARA ANALİZİ YAZ (reviews tablosuna) ----------
with engine.connect() as conn:
    # is_positive sütunu varsa sil ve tekrar oluştur
    conn.execute(text("ALTER TABLE reviews DROP COLUMN IF EXISTS is_positive;"))
    conn.execute(text("ALTER TABLE reviews ADD COLUMN is_positive INTEGER;"))

    for _, row in df.iterrows():
        update_query = text("""
            UPDATE reviews
            SET is_positive = :label
            WHERE id = :review_id
        """)
        conn.execute(update_query, {
            "label": int(row["is_positive"]),
            "review_id": int(row["id"])
        })
    conn.commit()

# ---------- ÜRÜNLERE OLUMLU YORUM ORANI YAZ (product_info tablosuna) ----------
# sentiment_score = 0 değerlerinin oranı (yani olumlu oranı)
summary = df.groupby("product_id")["is_positive"].apply(lambda x: (x == 0).sum() / len(x)).reset_index()
summary.columns = ["product_id", "sentiment_score"]

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE product_info DROP COLUMN IF EXISTS sentiment_score;"))
    conn.execute(text("ALTER TABLE product_info ADD COLUMN sentiment_score FLOAT;"))

    for _, row in summary.iterrows():
        update_query = text("""
            UPDATE product_info
            SET sentiment_score = :score
            WHERE id = :product_id
        """)
        conn.execute(update_query, {
            "score": float(row["sentiment_score"]),
            "product_id": int(row["product_id"])
        })
    conn.commit()

print("✅ Yorumlara sentiment etiketi eklendi ve ürün bazlı olumlu yorum oranı product_info tablosuna yazıldı.")
