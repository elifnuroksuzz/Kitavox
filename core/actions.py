# core/actions.py
import streamlit as st
import re
from datetime import datetime, timezone
from bson.objectid import ObjectId


# Modül importları
from core.database import (
    get_favorites_collection, 
    get_listening_history_collection, 
    get_users_collection,
    get_all_books_collection
)
from utils.helpers import extract_book_info, normalize_url, split_text_by_bytes
from utils.data_processing import download_and_process_pdf, extract_text_from_html
from components.audio_player import audio_player_component
# EKLENMESİ GEREKEN SATIR:
from .database import get_feedback_collection 

# --- Favori Aksiyonları ---
def add_to_favorites(user_id: str, book: dict):
    favorites_collection = get_favorites_collection()
    user_id_obj = ObjectId(user_id)
    book_url = book.get("url")
    display_title = book.get("title", "Bilinmeyen Kitap")
    
    if not book_url:
        st.error("Favorilere eklemek için kitap URL'si gerekli.")
        return

    existing = favorites_collection.find_one({"userId": user_id_obj, "bookUrl": book_url})
    if existing:
        st.warning(f"'{display_title}' zaten favorilerinizde.")
    else:
        fav_doc = {
            "userId": user_id_obj, "bookUrl": book_url, "bookName": display_title,
            "book_id": book.get("_id"), "normalizedUrl": normalize_url(book_url),
            "timestamp": datetime.now(timezone.utc)
        }
        favorites_collection.insert_one(fav_doc)
        st.success(f"'{display_title}' favorilere eklendi.")
        st.rerun()


def get_listening_history(user_id_str: str) -> list:
    history_collection = get_listening_history_collection()
    if history_collection is None: return []
    
    user_id_obj = ObjectId(user_id_str)
    # clean_duplicate_listening_history(user_id_obj) # Bu fonksiyonu daha sonra ekleyebilirsiniz
    return list(history_collection.find({"userId": user_id_obj}).sort("timestamp", -1))

def save_listening_progress(user_id: str, kitap_url: str, total_pages: int, current_page: int):
    """
    DÜZELTME: Bu fonksiyon artık veritabanında olmayan özel dokümanları da kaydedebilir.
    """
    history_collection = get_listening_history_collection()
    all_books_collection = get_all_books_collection()
    if history_collection is None or all_books_collection is None: return

    user_id_obj = ObjectId(user_id)
    
    # Kitap veritabanında var mı diye kontrol et
    book_in_db = all_books_collection.find_one({"url": kitap_url})
    
    # Bilgileri ayıkla
    if book_in_db:
        book_name = book_in_db.get("title", extract_book_info(kitap_url))
        author = book_in_db.get("author", "Bilinmiyor")
        category = book_in_db.get("category", "Bilinmiyor")
    else:
        # Eğer kitap veritabanında yoksa (özel URL/PDF), bilgileri URL'den al
        book_name = extract_book_info(kitap_url)
        author = "Özel Doküman"
        category = "Kişisel"

    progress = round((current_page / total_pages) * 100, 2) if total_pages > 0 else 0
    is_completed = current_page >= total_pages

    history_collection.update_one(
        {"userId": user_id_obj, "bookUrl": kitap_url},
        {"$set": {
            "userId": user_id_obj, "bookUrl": kitap_url, "bookName": book_name,
            "author": author, "category": category, # Yazar ve kategori de ekleniyor
            "normalizedUrl": normalize_url(kitap_url),
            "pageCount": total_pages, "currentPage": current_page,
            "readingProgress": progress, "isCompleted": is_completed,
            "timestamp": datetime.now(timezone.utc)
        }},
        upsert=True # Eğer kayıt yoksa oluştur
    )

def set_selected_book(book_dict: dict, source: str):
    st.session_state["selected_book"] = book_dict
    st.session_state["selected_book_source"] = source
    st.rerun()

def start_listening_process(user_id_str: str):
    # ... (Bu fonksiyonun geri kalanı aynı)
    if "selected_book" in st.session_state and st.session_state.selected_book:
        book = st.session_state.selected_book
        user_id_obj = ObjectId(user_id_str)

        users_collection = get_users_collection()
        user = users_collection.find_one({"_id": user_id_obj})
        user_preferences = user.get("preferences", {})
        
        history_key_url = book.get("url")
        
        history_collection = get_listening_history_collection()
        history = history_collection.find_one({"userId": user_id_obj, "bookUrl": history_key_url}) if history_key_url else None
        
        start_page = book.get("start_page", history.get("currentPage", 1) if history else 1)
        
        kitap_url_to_process = book.get("pdf_url") or book.get("url")
        
        if not kitap_url_to_process:
            st.error("İşlenecek bir URL veya dosya yolu bulunamadı.")
            st.session_state.pop('selected_book', None)
            return

        is_pdf = kitap_url_to_process.lower().endswith(".pdf")

        pages = []
        physical_pages_total = 0

        with st.spinner("Kitap içeriği hazırlanıyor..."):
            if is_pdf:
                pages_text, physical_pages_total_from_pdf = download_and_process_pdf(kitap_url_to_process)
                pages = []
                for page_content in pages_text:
                    pages.extend(split_text_by_bytes(page_content))
                physical_pages_total = len(pages)
            else:
                text = extract_text_from_html(kitap_url_to_process)
                pages = split_text_by_bytes(text)
                physical_pages_total = len(pages)
        
        if not pages:
            st.error("İçerik okunamadı. Lütfen başka bir kaynak deneyin.")
            st.session_state.pop('selected_book', None)
            return

        import components.audio_player
        components.audio_player.dinleme_gecmisi_ekle = save_listening_progress

        components.audio_player.audio_player_component(
            pages=pages,
            user_preferences=user_preferences,
            user_id=user_id_str,
            kitap_url=history_key_url,
            start_page=start_page - 1,
            physical_pages_total=physical_pages_total,
            book_name=book["title"]
        )


# --- Dinleme Geçmişi Aksiyonları ---
def clean_duplicate_listening_history(user_id_obj: ObjectId):
    history_collection = get_listening_history_collection()
    if history_collection is None: return
    
    pipeline = [
        {"$match": {"userId": user_id_obj}},
        {"$group": {
            "_id": {"bookUrl": "$bookUrl"},
            "docs": {"$push": {"_id": "$_id", "timestamp": "$timestamp"}}
        }},
        {"$match": {"docs.1": {"$exists": True}}} # Birden fazla olanları bul
    ]
    duplicates = list(history_collection.aggregate(pipeline))
    
    for group in duplicates:
        docs = sorted(group['docs'], key=lambda x: x['timestamp'], reverse=True)
        ids_to_delete = [doc['_id'] for doc in docs[1:]] # En sonuncusu hariç hepsini sil
        history_collection.delete_many({"_id": {"$in": ids_to_delete}})

def get_listening_history(user_id_str: str) -> list:
    history_collection = get_listening_history_collection()
    if history_collection is None: return []
    
    user_id_obj = ObjectId(user_id_str)
    clean_duplicate_listening_history(user_id_obj)
    return list(history_collection.find({"userId": user_id_obj}).sort("timestamp", -1))

def save_listening_progress(user_id: str, kitap_url: str, total_pages: int, current_page: int):
    history_collection = get_listening_history_collection()
    if history_collection is None: return

    user_id_obj = ObjectId(user_id)
    book_name = extract_book_info(kitap_url)
    progress = round((current_page / total_pages) * 100, 2) if total_pages > 0 else 0
    is_completed = current_page >= total_pages

    history_collection.update_one(
        {"userId": user_id_obj, "bookUrl": kitap_url},
        {"$set": {
            "userId": user_id_obj, "bookUrl": kitap_url, "bookName": book_name,
            "normalizedUrl": normalize_url(kitap_url),
            "pageCount": total_pages, "currentPage": current_page,
            "readingProgress": progress, "isCompleted": is_completed,
            "timestamp": datetime.now(timezone.utc)
        }},
        upsert=True
    )

# --- Dinleme Süreci Yönetimi ---
def set_selected_book(book_dict: dict, source: str):
    st.session_state["selected_book"] = book_dict
    st.session_state["selected_book_source"] = source
    st.rerun()

# core/actions.py içindeki start_listening_process fonksiyonunun GÜNCELLENMİŞ hali

def start_listening_process(user_id_str: str):
    """
    Session state'te seçili bir kitap varsa dinleme sürecini başlatır.
    Bu fonksiyon artık veritabanında olmayan geçici kitap sözlüklerini de işleyebilir.
    """
    if "selected_book" in st.session_state and st.session_state.selected_book:
        book = st.session_state.selected_book
        user_id_obj = ObjectId(user_id_str)

        users_collection = get_users_collection()
        user = users_collection.find_one({"_id": user_id_obj})
        user_preferences = user.get("preferences", {})
        
        # Kitabın URL'si dinleme geçmişi için anahtar olacak
        history_key_url = book.get("url")
        
        history_collection = get_listening_history_collection()
        history = history_collection.find_one({"userId": user_id_obj, "bookUrl": history_key_url}) if history_key_url else None
        
        # Session state'den gelen başlangıç sayfasını öncelikli yap (örn: "kaldığım yerden devam et")
        start_page = book.get("start_page", history.get("currentPage", 1) if history else 1)
        
        kitap_url_to_process = book.get("pdf_url") or book.get("url")
        
        if not kitap_url_to_process:
            st.error("İşlenecek bir URL veya dosya yolu bulunamadı.")
            st.session_state.pop('selected_book', None)
            return

        is_pdf = kitap_url_to_process.lower().endswith(".pdf")

        pages = []
        physical_pages_total = 0

        with st.spinner("Kitap içeriği hazırlanıyor..."):
            if is_pdf:
                # Eğer geçici bir dosya yolu ise (yükleme için)
                if book.get("is_temp_file", False):
                    # download_and_process_pdf zaten dosya yoluyla çalışabiliyor
                    pages, physical_pages_total = download_and_process_pdf(kitap_url_to_process)
                else: # URL ise
                    pages, physical_pages_total = download_and_process_pdf(kitap_url_to_process)
            else: # Web sayfası ise
                text = extract_text_from_html(kitap_url_to_process)
                pages = split_text_by_bytes(text)
                physical_pages_total = len(pages)
        
        if not pages:
            st.error("İçerik okunamadı. Lütfen başka bir kaynak deneyin.")
            st.session_state.pop('selected_book', None)
            return

        import components.audio_player
        components.audio_player.dinleme_gecmisi_ekle = save_listening_progress

        components.audio_player.audio_player_component(
            pages=pages,
            user_preferences=user_preferences,
            user_id=user_id_str,
            kitap_url=history_key_url, # Geçmiş kaydı için ana URL'yi kullan
            start_page=start_page - 1,
            physical_pages_total=physical_pages_total,
            book_name=book["title"]
        )

# core/actions.py dosyasının sonuna eklenecek yeni fonksiyonlar:

def submit_feedback(user_id: str, book_url: str, rating: int, comment: str, feedback_id_str: str = None):
    """Yeni geri bildirim ekler veya mevcut olanı günceller."""
    feedback_collection = get_feedback_collection()
    if feedback_collection is None:
        st.error("Veritabanı bağlantısı kurulamadı.")
        return False
    
    user_id_obj = ObjectId(user_id)
    feedback_data = {
        "userId": user_id_obj,
        "bookUrl": book_url,
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.now(timezone.utc)
    }
    
    try:
        if feedback_id_str: # Güncelleme modu
            feedback_collection.update_one(
                {"_id": ObjectId(feedback_id_str)},
                {"$set": {
                    "rating": rating,
                    "comment": comment,
                    "timestamp": datetime.now(timezone.utc)
                }}
            )
            st.success("Geri bildiriminiz güncellendi!")
        else: # Ekleme modu
            feedback_collection.insert_one(feedback_data)
            st.success("Geri bildiriminiz için teşekkürler!")
        return True
    except Exception as e:
        st.error(f"Geri bildirim işlenirken hata oluştu: {e}")
        return False

def delete_feedback(feedback_id_str: str):
    """Verilen ID'ye sahip geri bildirimi siler."""
    feedback_collection = get_feedback_collection()
    if feedback_collection is None:
        st.error("Veritabanı bağlantısı kurulamadı.")
        return False
        
    try:
        result = feedback_collection.delete_one({"_id": ObjectId(feedback_id_str)})
        if result.deleted_count > 0:
            st.success("Geri bildirim silindi.")
            return True
        else:
            st.warning("Silinecek geri bildirim bulunamadı.")
            return False
    except Exception as e:
        st.error(f"Geri bildirim silinirken hata oluştu: {e}")
        return False