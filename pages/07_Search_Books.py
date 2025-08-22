# pages/07_Search_Books.py
import streamlit as st
import re
from bson.objectid import ObjectId

from core.database import get_all_books_collection
from core.actions import add_to_favorites, set_selected_book, start_listening_process



if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın."); st.page_link("streamlit_app.py", label="Giriş Sayfasına Git"); st.stop()

def search_page(user_id_str: str):
    st.title("🔍 Kitaplarda Arama Yap")
    
    # Eğer bir kitap dinleniyorsa, arama arayüzünü gösterme
    if "selected_book" in st.session_state and st.session_state.selected_book:
        start_listening_process(user_id_str)
        return

    all_books_collection = get_all_books_collection()
    
    search_term = st.text_input("Kitap adı, yazar veya kategori girin:", key="search_term_input")
    
    if search_term:
        # Arama sorgusunu oluştur (büyük/küçük harf duyarsız)
        query = {"$or": [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"author": {"$regex": search_term, "$options": "i"}},
            {"category": {"$regex": search_term, "$options": "i"}},
        ]}
        
        results = list(all_books_collection.find(query).limit(20))
        
        if not results:
            st.warning("Aramanızla eşleşen bir kitap bulunamadı.")
        else:
            st.success(f"{len(results)} kitap bulundu.")
            for book in results:
                display_title = book.get("title", "Başlık Bilinmiyor")
                cover_image = book.get("cover_image_url", "https://www.cihatayaz.com/wp-content/uploads/2017/06/slider_item_01.gif")

                st.markdown("---")
                col1, col2, col3 = st.columns([1, 3, 1])

                with col1:
                    st.image(cover_image, width=100)

                with col2:
                    st.subheader(display_title)
                    st.caption(f"Yazar: {book.get('author', 'Bilinmiyor')} | Kategori: {book.get('category', 'Bilinmiyor')}")

                with col3:
                    if st.button("🎧 Dinle", key=f"search_listen_{book['_id']}"):
                        set_selected_book(book, source="search")
                    
                    if st.button("❤️ Favorilere Ekle", key=f"search_fav_{book['_id']}"):
                        add_to_favorites(user_id_str, book)

# --- Sayfayı Çalıştır ---
search_page(st.session_state.user_id)