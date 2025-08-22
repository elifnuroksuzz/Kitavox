# core/recommender.py

import streamlit as st
from bson.objectid import ObjectId
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Modül importları
from core.database import (
    get_listening_history_collection,
    get_favorites_collection,
    get_feedback_collection,
    get_all_books_collection
)

# --- ANA ÖNERİ FONKSİYONU ---

@st.cache_data(ttl=900) # Önerileri 15 dakika cache'le
def get_enhanced_recommendations(user_id_str: str, n_recommendations=5):
    """
    Kullanıcının geçmişi, favorileri ve geri bildirimlerini analiz ederek
    gelişmiş ve kişiselleştirilmiş kitap önerileri oluşturur.
    """
    try:
        user_id = ObjectId(user_id_str)
        
        # Gerekli koleksiyonları al
        history_collection = get_listening_history_collection()
        favorites_collection = get_favorites_collection()
        feedback_collection = get_feedback_collection()
        all_books_collection = get_all_books_collection()

        if any(c is None for c in [history_collection, favorites_collection, feedback_collection, all_books_collection]):
            st.error("Veritabanı bağlantı sorunu nedeniyle öneriler alınamıyor.")
            return []

        # Kullanıcı verilerini topla
        user_history = list(history_collection.find({"userId": user_id}))
        user_favorites = list(favorites_collection.find({"userId": user_id}))
        user_feedback = list(feedback_collection.find({"userId": user_id}))

        # Kullanıcı tercihlerini (kategori ve yazar puanları) hesapla
        preferred_categories = {}
        preferred_authors = {}
        
        # Geçmişten gelenler (ağırlık: 1)
        for entry in user_history:
            book = all_books_collection.find_one({"url": entry.get("bookUrl")})
            if book:
                if book.get("category"): preferred_categories[book["category"]] = preferred_categories.get(book["category"], 0) + 1
                if book.get("author"): preferred_authors[book["author"]] = preferred_authors.get(book["author"], 0) + 1
        
        # Favorilerden gelenler (ağırlık: 2)
        for fav in user_favorites:
            book = all_books_collection.find_one({"url": fav.get("bookUrl")})
            if book:
                if book.get("category"): preferred_categories[book["category"]] = preferred_categories.get(book["category"], 0) + 2
                if book.get("author"): preferred_authors[book["author"]] = preferred_authors.get(book["author"], 0) + 2

        # Geri bildirimlerden gelenler (ağırlık: puana göre -2 ile +2 arası)
        for fb in user_feedback:
            book = all_books_collection.find_one({"url": fb.get("bookUrl")})
            if book:
                weight = fb.get("rating", 3) - 3
                if book.get("category"): preferred_categories[book["category"]] = preferred_categories.get(book["category"], 0) + weight
                if book.get("author"): preferred_authors[book["author"]] = preferred_authors.get(book["author"], 0) + weight

        # Eğer hiç tercih verisi yoksa, popüler kitapları döndür
        if not preferred_categories and not preferred_authors:
            return get_popular_books(limit=n_recommendations)

        # Okunmuş kitapları ayıkla
        read_urls = {entry.get("bookUrl") for entry in user_history}
        
        # Okunmamış tüm kitapları al
        candidate_books = list(all_books_collection.find({"url": {"$nin": list(read_urls)}}))
        
        # Kitapları puanla
        scored_books = []
        for book in candidate_books:
            score = 0
            score += preferred_categories.get(book.get("category"), 0) * 2 # Kategori eşleşme puanı
            score += preferred_authors.get(book.get("author"), 0) * 3 # Yazar eşleşme puanı
            if score > 0:
                scored_books.append((book, score))

        # En yüksek puanlı kitapları seç
        scored_books.sort(key=lambda x: x[1], reverse=True)
        recommendations = [book for book, score in scored_books[:n_recommendations]]

        # Yeterli öneri yoksa popüler olanlarla tamamla
        if len(recommendations) < n_recommendations:
            popular_books = get_popular_books(limit=n_recommendations)
            for book in popular_books:
                if len(recommendations) < n_recommendations and not any(r['_id'] == book['_id'] for r in recommendations):
                    recommendations.append(book)

        return recommendations

    except Exception as e:
        st.error(f"Öneriler oluşturulurken bir hata oluştu: {e}")
        return get_popular_books(limit=n_recommendations) # Hata durumunda popülerleri göster

# --- YARDIMCI ÖNERİ FONKSİYONLARI ---

@st.cache_data(ttl=1800)
def get_popular_books(limit=10):
    """Genel olarak en çok dinlenen veya favorilere eklenen kitapları döndürür."""
    history_collection = get_listening_history_collection()
    all_books_collection = get_all_books_collection()

    if history_collection is None or all_books_collection is None:
        return []

    pipeline = [
        {"$group": {"_id": "$bookUrl", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    popular_urls = [doc["_id"] for doc in history_collection.aggregate(pipeline)]
    
    return list(all_books_collection.find({"url": {"$in": popular_urls}}))
