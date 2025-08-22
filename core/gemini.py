# core/gemini.py
import os
import streamlit as st
import requests
from dotenv import load_dotenv
from core.database import get_all_books_collection
import re

load_dotenv()

class GeminiAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
    
    def generate_content(self, prompt: str):
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        except requests.exceptions.RequestException as e:
            st.error(f"API hatası: {e}")
            return f"API ile iletişim kurarken bir hata oluştu: {e}"
        except (KeyError, IndexError):
            st.warning("API'den beklenen formatta bir yanıt alınamadı.")
            return "Geçerli bir yanıt alınamadı."

@st.cache_resource
def initialize_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.warning("GEMINI_API_KEY bulunamadı. Yapay zeka özellikleri devre dışı kalacak.")
        return None
    return GeminiAPI(api_key)

def get_book_summary(gemini: GeminiAPI, book_title: str) -> str:
    if not gemini: return "AI servisi mevcut değil."
    
    all_books_collection = get_all_books_collection()
    if all_books_collection is None: return "Veritabanı bağlantısı yok."

    book_data = all_books_collection.find_one({"title": {"$regex": book_title, "$options": "i"}})
    
    if book_data and book_data.get("description"):
        return book_data["description"]

    prompt = (
        f"Lütfen '{book_title}' adlı kitap hakkında, ana temasını ve konusunu anlatan, "
        f"yaklaşık 100 kelimelik, akıcı ve bilgilendirici bir özet yaz. "
        f"Eğer kitap hakkında yeterli bilgin yoksa, bu konuda yeterli bilgiye sahip olmadığını belirt."
    )
    return gemini.generate_content(prompt)

def answer_book_question(gemini: GeminiAPI, book_title: str, author: str, question: str) -> str:
    if not gemini: return "AI servisi mevcut değil."

    prompt = (
        f"Aşağıdaki kitap hakkında sorulan soruyu cevapla. Cevabın kısa, öz ve sadece bu kitaba özel olsun.\n"
        f"Kitap Adı: '{book_title}'\n"
        f"Yazar: {author}\n"
        f"Soru: '{question}'\n\n"
        f"Cevap:"
    )
    return gemini.generate_content(prompt)