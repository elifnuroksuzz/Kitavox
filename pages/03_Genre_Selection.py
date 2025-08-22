# pages/03_📚_Tür_Seçimi.py
import streamlit as st
from PIL import Image
import os
import logging
from urllib.parse import urljoin



# Modül importları
from core.actions import set_selected_book, start_listening_process, add_to_favorites
from core.database import get_all_books_collection
from utils.data_processing import fetch_page
from components.header import render_header
from components.footer import render_footer

# Oturum Kontrolü
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın."); st.page_link("streamlit_app.py", label="Giriş Sayfasına Git"); st.stop()

def display_genres():
    """Siteden türleri çeker ve butonlar halinde gösterir."""
    st.subheader("İstediğiniz Türü Seçin")
    
    tur_resimleri = {
        "Roman": "roman.jpg", "Şiir": "şiir.jpg", "Öykü": "öykü.jpg"
    }
    istenen_turler = {"Roman", "Şiir", "Öykü"}
    
    soup = fetch_page("/")
    if not soup:
        st.error("Türler alınamadı. Lütfen daha sonra tekrar deneyin.")
        return

    cols = st.columns(len(istenen_turler))
    col_idx = 0
    found_genres = set()

    for a in soup.find_all("a", href=True):
        tur_adi = a.get_text(strip=True)
        if tur_adi in istenen_turler and tur_adi not in found_genres:
            with cols[col_idx]:
                image_path = tur_resimleri.get(tur_adi)
                if image_path and os.path.exists(image_path):
                    st.image(image_path, caption=tur_adi)
                
                if st.button(f"{tur_adi} Kitaplarını Gör", key=f"genre_{tur_adi}"):
                    st.session_state.selected_genre_name = tur_adi
                    st.session_state.selected_genre_url = a['href']
                    st.rerun()
            col_idx += 1
            found_genres.add(tur_adi)
            if len(found_genres) == len(istenen_turler): break

def display_books_for_genre(user_id_str, genre_name, genre_url):
    """Seçilen türe ait kitapları siteden çeker ve listeler."""
    st.subheader(f"'{genre_name}' Türündeki Kitaplar")

    all_books_collection = get_all_books_collection()
    
    with st.spinner(f"'{genre_name}' türündeki kitaplar yükleniyor..."):
        soup = fetch_page(genre_url)
        if not soup:
            st.error("Kitaplar alınamadı."); return

        # DÜZELTME: Web sitesinin yapısı değişmiş olabileceğinden, kitapları bulmak için
        # daha genel ve güvenilir bir yöntem kullanıyoruz. 'card-action' içindeki linkleri arıyoruz.
        kitap_linkleri = soup.select("div.card-action a[href]")
        
        if not kitap_linkleri:
            st.warning("Bu türde gösterilecek kitap bulunamadı veya site yapısı değişti.")
            return

        kitap_sayaci = 0
        for title_a in kitap_linkleri:
            try:
                # Tam URL'yi oluştur
                kitap_url = urljoin("https://dijitalkitaplar.net", title_a['href'])
                
                # Veritabanından bu URL ile eşleşen zenginleştirilmiş veriyi bul
                book = all_books_collection.find_one({"url": kitap_url})

                # Eğer kitap veritabanında yoksa, bu adımı atla
                if not book:
                    continue
                
                kitap_sayaci += 1
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
                    if st.button("🎧 Dinle", key=f"genre_listen_{book['_id']}"):
                        set_selected_book(book, source="genre")
                    if st.button("❤️ Favorilere Ekle", key=f"genre_fav_{book['_id']}"):
                        add_to_favorites(user_id_str, book)
            except Exception as e:
                logging.warning(f"Bir kitap işlenirken hata oluştu: {e}")
                continue
        
        if kitap_sayaci == 0:
            st.warning("Bu türdeki kitaplar veritabanımızda henüz bulunmuyor.")


def main():
    """Bu sayfanın ana yönlendiricisi."""
    user_id = st.session_state.user_id
    
    if "selected_book" in st.session_state and st.session_state.selected_book:
        start_listening_process(user_id)
        return

    render_header()
    st.title("📚 Türlere Göre Kitap Keşfet")

    if 'selected_genre_name' in st.session_state and st.session_state.selected_genre_name:
        if st.button("← Tüm Türlere Geri Dön"):
            st.session_state.selected_genre_name = None
            st.session_state.selected_genre_url = None
            st.rerun()
        
        display_books_for_genre(
            user_id,
            st.session_state.selected_genre_name,
            st.session_state.selected_genre_url
        )
    else:
        display_genres()
    
    render_footer()

# --- Sayfayı Çalıştır ---
main()
