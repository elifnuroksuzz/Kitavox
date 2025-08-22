# pages/02_📄_Özel_Doküman_Yükle.py
import streamlit as st
import os
from bson.objectid import ObjectId

# Modül importları
from core.actions import get_listening_history, set_selected_book, start_listening_process
from utils.helpers import extract_book_info
from components.header import render_header


# Oturum Kontrolü
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın."); st.page_link("streamlit_app.py", label="Giriş Sayfasına Git"); st.stop()

# DÜZELTME: Kalıcı dosya saklama dizini
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def upload_document_page_content(user_id_str: str):
    render_header()
    st.title("📄 Özel Doküman Yükle ve Seslendir")

    choice = st.selectbox(
        "Hangi türde içerik seslendirmek istersiniz?",
        ["Seçim Yapın...", "Web Sayfası URL'si", "Bilgisayarımdan PDF Dosyası"]
    )

    if choice == "Web Sayfası URL'si":
        # ... (Bu kısım aynı kalır) ...
        st.subheader("Web Sayfası URL'si ile Seslendirme")
        url = st.text_input("Lütfen bir web sayfası adresi (URL) girin:")
        if url:
            history = get_listening_history(user_id_str)
            url_history = next((item for item in history if item.get("bookUrl") == url), None)
            start_page = 1
            if url_history:
                st.info(f"Bu adresi daha önce dinlemişsiniz. Sayfa {url_history['currentPage']}/{url_history['pageCount']} üzerinde durmuşsunuz.")
                c1, c2 = st.columns(2)
                if c1.button("Kaldığım Yerden Devam Et"):
                    start_page = url_history['currentPage']
                if c2.button("En Baştan Başla"):
                    start_page = 1
            if st.button("Seslendir"):
                book_title = extract_book_info(url)
                temp_book = {"title": book_title, "url": url, "pdf_url": url if url.lower().endswith(".pdf") else None, "start_page": start_page, "is_temp_file": False}
                set_selected_book(temp_book, source="custom_url")

    elif choice == "Bilgisayarımdan PDF Dosyası":
        st.subheader("PDF Dosyası Yükleyerek Seslendirme")
        uploaded_file = st.file_uploader("Lütfen bir PDF dosyası seçin", type="pdf")

        if uploaded_file is not None:
            # DÜZELTME: Dosyayı geçici bir yere değil, kalıcı olarak uploads klasörüne kaydet.
            # Dosya adını benzersiz yap (kullanıcıID_dosyaadı)
            permanent_filename = f"{user_id_str}_{uploaded_file.name}"
            permanent_file_path = os.path.join(UPLOAD_DIR, permanent_filename)
            
            with open(permanent_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            history_key = uploaded_file.name # Geçmişte hala orijinal adıyla görünecek
            history = get_listening_history(user_id_str)
            file_history = next((item for item in history if item.get("bookUrl") == history_key), None)

            start_page = 1
            if file_history:
                st.info(f"Bu dosyayı daha önce dinlemişsiniz. Sayfa {file_history['currentPage']}/{file_history['pageCount']} üzerinde durmuşsunuz.")
                c1, c2 = st.columns(2)
                if c1.button("Kaldığım Yerden Devam Et"):
                    start_page = file_history['currentPage']
                if c2.button("En Baştan Başla"):
                    start_page = 1

            if st.button("Yüklenen Dosyayı Seslendir"):
                book_title = extract_book_info(uploaded_file.name)
                temp_book = {
                    "title": book_title,
                    "url": history_key, # Geçmiş kaydı için orijinal dosya adını kullan
                    "pdf_url": permanent_file_path, # İşlenecek olan KALICI dosyanın yolu
                    "start_page": start_page,
                    "is_temp_file": True 
                }
                set_selected_book(temp_book, source="custom_pdf")
    
    

def main():
    user_id = st.session_state.user_id
    if "selected_book" in st.session_state and st.session_state.selected_book:
        start_listening_process(user_id)
    else:
        upload_document_page_content(user_id)

main()
