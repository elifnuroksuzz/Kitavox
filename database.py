# core/database.py

import os
import streamlit as st
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

@st.cache_resource
def get_db_connection():
    """
    MongoDB bağlantısını kurar ve döndürür.
    Streamlit'in cache_resource'u ile bağlantının tekrar tekrar kurulmasını engeller.
    """
    try:
        MONGO_URI = os.getenv("MONGO_URI")
        if not MONGO_URI:
            raise ValueError("MONGO_URI ortam değişkeni bulunamadı. Lütfen .env dosyasını kontrol edin.")
            
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        # Bağlantıyı test et
        client.admin.command("ping")
        print("MongoDB bağlantısı başarılı.")
        return client["Sesli_Kitap"]
    except Exception as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

# Veritabanı bağlantısını al
DB = get_db_connection()

# Koleksiyonları döndüren fonksiyonlar
def get_users_collection():
    return DB["users"] if DB else None

def get_books_collection():
    return DB["books"] if DB else None

def get_listening_history_collection():
    return DB["ListeningHistory"] if DB else None

def get_favorites_collection():
    return DB["favorites_books"] if DB else None

def get_all_books_collection():
    return DB["all_books"] if DB else None

def get_feedback_collection():
    return DB["feedback"] if DB else None