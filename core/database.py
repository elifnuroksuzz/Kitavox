# core/database.py

import os
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_db_connection():
    try:
        MONGO_URI = os.getenv("MONGO_URI")
        if not MONGO_URI:
            raise ValueError("MONGO_URI ortam değişkeni .env dosyasında bulunamadı.")
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        client.admin.command("ping")
        print("MongoDB bağlantısı başarılı.")
        return client["Sesli_Kitap"]
    except Exception as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        return None

DB = get_db_connection()

# DÜZELTME: Tüm koleksiyon fonksiyonlarında 'if DB' yerine 'if DB is not None' kullanıldı.
def get_users_collection(): return DB["users"] if DB is not None else None
def get_books_collection(): return DB["books"] if DB is not None else None
def get_listening_history_collection(): return DB["ListeningHistory"] if DB is not None else None
def get_favorites_collection(): return DB["favorites_books"] if DB is not None else None
def get_all_books_collection(): return DB["all_books"] if DB is not None else None
def get_feedback_collection(): return DB["feedback"] if DB is not None else None