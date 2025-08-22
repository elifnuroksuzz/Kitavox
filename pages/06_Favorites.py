# pages/06_Favorites.py
import streamlit as st
from bson.objectid import ObjectId
import re

from core.database import get_favorites_collection, get_all_books_collection
from core.actions import set_selected_book, start_listening_process, add_to_favorites # add_to_favorites burada kullanılmayacak ama import kalabilir
from utils.helpers import normalize_url



if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın."); st.page_link("streamlit_app.py", label="Giriş Sayfasına Git"); st.stop()

def favorites_page(user_id_str: str):
    st.title("❤️ Favori Kitaplarım")

    # Eğer bir kitap dinleniyorsa, favori listesini gösterme
    if "selected_book" in st.session_state and st.session_state.selected_book:
        start_listening_process(user_id_str)
        return

    user_id_obj = ObjectId(user_id_str)
    favorites_collection = get_favorites_collection()
    all_books_collection = get_all_books_collection()
    
    favorites = list(favorites_collection.find({"userId": user_id_obj}).sort("timestamp", -1))

    if not favorites:
        st.info("Henüz favorilerinize eklediğiniz bir kitap bulunmuyor.")
        st.page_link("pages/07_Search_Books.py", label="Kitap Aramak İçin Tıklayın")
        return

    for fav in favorites:
        book = all_books_collection.find_one({"url": fav["bookUrl"]})
        if not book: continue

        display_title = book.get("title", fav.get("bookName", "Başlık Bilinmiyor"))
        cover_image = book.get("cover_image_url", "https://www.cihatayaz.com/wp-content/uploads/2017/06/slider_item_01.gif")

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            st.image(cover_image, width=100)

        with col2:
            st.subheader(display_title)
            st.caption(f"Yazar: {book.get('author', 'Bilinmiyor')} | Kategori: {book.get('category', 'Bilinmiyor')}")

        with col3:
            if st.button("🎧 Dinle", key=f"listen_{fav['_id']}", help="Kitabı dinlemeye başla"):
                set_selected_book(book, source="favorites")
            
            if st.button("🗑️ Çıkar", key=f"remove_{fav['_id']}", help="Favorilerden kaldır"):
                favorites_collection.delete_one({"_id": fav["_id"]})
                st.success(f"'{display_title}' favorilerden çıkarıldı.")
                st.rerun()

# --- Sayfayı Çalıştır ---
favorites_page(st.session_state.user_id)