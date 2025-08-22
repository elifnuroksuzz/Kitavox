# pages/10_Feedback.py

"""
Bu sayfa, kullanıcıların dinledikleri kitaplar hakkında geri bildirim
bırakmalarını, görüntülemelerini, düzenlemelerini ve silmelerini sağlar.
Arayüz, her bir geri bildirimi görsel bir kart içinde sunar.
"""

# -----------------------------------------------------------------------------
# Gerekli Kütüphane ve Modüllerin Import Edilmesi
# -----------------------------------------------------------------------------
import streamlit as st
from bson.objectid import ObjectId
from datetime import datetime

# Proje içi modüllerin import edilmesi
from core.actions import get_listening_history, submit_feedback, delete_feedback
from core.database import get_feedback_collection
from components.header import render_header
from components.footer import render_footer

# -----------------------------------------------------------------------------
# Sayfa Yapılandırması ve Oturum Kontrolü
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Geri Bildirimler - Kitavox",
    page_icon="💬"
)

# Oturum kontrolü
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın.")
    st.page_link("streamlit_app.py", label="Giriş Sayfasına Git", icon="🏠")
    st.stop()

# -----------------------------------------------------------------------------
# Yardımcı Fonksiyonlar
# -----------------------------------------------------------------------------

def get_user_book_data(user_id: str):
    """
    Kullanıcının dinleme geçmişindeki tüm kitapların detaylı bilgilerini
    (kapak, yazar vb.) tek seferde çeker ve haritalar oluşturur.
    Bu, sayfa içinde tekrarlanan veritabanı sorgularını önler.
    """
    history = get_listening_history(user_id)
    if not history:
        return {}, {}

    # bookUrl -> {bookData} ve bookName -> {bookData} haritalarını oluştur
    url_to_book_map = {}
    title_to_book_map = {}

    for entry in history:
        # Kitap bilgilerini oluştururken eksik verilere karşı hazırlıklı olalım
        book_data = {
            "title": entry.get("bookName", "Bilinmeyen Başlık"),
            "url": entry.get("bookUrl", ""),
            "cover_image": entry.get("cover_image_url", "https://img.icons8.com/plasticine/100/document.png"),
            "author": entry.get("author", "Bilinmiyor"),
            "category": entry.get("category", "Belirtilmemiş")
        }
        
        # Eğer bir URL varsa ve bu URL haritada yoksa ekle
        if book_data["url"] and book_data["url"] not in url_to_book_map:
            url_to_book_map[book_data["url"]] = book_data
        
        # Eğer bir başlık varsa ve bu başlık haritada yoksa ekle
        if book_data["title"] and book_data["title"] not in title_to_book_map:
            title_to_book_map[book_data["title"]] = book_data
            
    return url_to_book_map, title_to_book_map

def display_stars(rating: int, total_stars: int = 5) -> str:
    """Verilen puana göre dolu ve boş yıldızları string olarak döndürür."""
    return "⭐" * rating + "☆" * (total_stars - rating)

# -----------------------------------------------------------------------------
# Sayfa Ana Fonksiyonu
# -----------------------------------------------------------------------------

def feedback_page():
    """Geri bildirim sayfasının ana arayüzünü oluşturur."""
    
    render_header()
    st.title("💬 Geri Bildirimleriniz")
    st.markdown("Dinlediğiniz kitaplar hakkındaki düşünceleriniz bizim için değerli. Buradan yorumlarınızı paylaşabilir ve düzenleyebilirsiniz.")

    user_id = st.session_state.user_id
    feedback_collection = get_feedback_collection()
    user_id_obj = ObjectId(user_id)

    # Düzenleme modu için session state
    if 'editing_feedback_id' not in st.session_state:
        st.session_state.editing_feedback_id = None

    # Gerekli tüm kitap verilerini sayfanın başında tek seferde al
    url_to_book_map, title_to_book_map = get_user_book_data(user_id)

    col1, col2 = st.columns([2, 3])

    # --- SOL SÜTUN: Form Alanı ---
    with col1:
        # DÜZENLEME FORMU
        if st.session_state.editing_feedback_id:
            st.subheader("Geri Bildirimi Düzenle")
            feedback_to_edit = feedback_collection.find_one({"_id": ObjectId(st.session_state.editing_feedback_id)})
            book_data = url_to_book_map.get(feedback_to_edit['bookUrl'])

            if book_data:
                st.image(book_data['cover_image'], width=80)
                st.info(f"**Kitap:** {book_data['title']}")

            with st.form("edit_form"):
                rating = st.slider("Yeni Puanınız", 1, 5, feedback_to_edit.get('rating', 3), format="%d ⭐")
                comment = st.text_area("Yeni Yorumunuz:", value=feedback_to_edit.get('comment', ''), height=150)
                
                submitted = st.form_submit_button("Değişiklikleri Kaydet", type="primary")
                if submitted:
                    submit_feedback(user_id, feedback_to_edit['bookUrl'], rating, comment, st.session_state.editing_feedback_id)
                    st.session_state.editing_feedback_id = None
                    st.success("Geri bildiriminiz güncellendi!")
                    st.rerun()
            
            if st.button("Düzenlemeyi İptal Et"):
                st.session_state.editing_feedback_id = None
                st.rerun()
        
        # YENİ GERİ BİLDİRİM FORMU
        else:
            st.subheader("Yeni Geri Bildirim Bırak")
            if not title_to_book_map:
                st.warning("Geri bildirim bırakabilmek için önce bir kitap dinlemelisiniz.")
            else:
                sorted_titles = sorted(list(title_to_book_map.keys()))
                selected_title = st.selectbox("Hangi kitap için geri bildirim bırakmak istersiniz?", options=sorted_titles)

                if selected_title:
                    book_data = title_to_book_map[selected_title]
                    st.image(book_data['cover_image'], width=80)
                    st.caption(f"Yazar: {book_data['author']} | Kategori: {book_data['category']}")

                with st.form("feedback_form"):
                    rating = st.slider("Puanınız", 1, 5, 3, format="%d ⭐")
                    comment = st.text_area("Yorumunuz (isteğe bağlı):", height=150)
                    submitted = st.form_submit_button("Geri Bildirimi Gönder", type="primary")
                    
                    if submitted and selected_title:
                        selected_url = title_to_book_map[selected_title]["url"]
                        submit_feedback(user_id, selected_url, rating, comment)
                        st.success("Geri bildiriminiz için teşekkür ederiz!")
                        st.rerun()

    # --- SAĞ SÜTUN: Geri Bildirim Listesi ---
    with col2:
        st.subheader("Önceki Geri Bildirimleriniz")
        feedbacks = list(feedback_collection.find({"userId": user_id_obj}).sort("timestamp", -1))

        if not feedbacks:
            st.info("Henüz hiç geri bildirim bırakmadınız.")
        else:
            for fb in feedbacks:
                book_data = url_to_book_map.get(fb['bookUrl'])
                
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    # Kitap Resmi
                    with c1:
                        if book_data:
                            st.image(book_data['cover_image'], width=80)
                        else:
                            st.image("https://img.icons8.com/plasticine/100/document.png", width=80) # Varsayılan resim
                    
                    # Kitap ve Geri Bildirim Detayları
                    with c2:
                        if book_data:
                            st.subheader(book_data['title'])
                            st.caption(f"{book_data['author']} | {book_data['category']}")
                        else:
                            st.subheader("Bilinmeyen Kitap")
                        
                        st.write(f"**Puanınız:** {display_stars(fb.get('rating', 0))}")
                    
                    st.markdown(f"**Yorumunuz:**\n> *{fb.get('comment', 'Yorum bırakılmamış.')}*")
                    
                    # Butonlar ve Tarih
                    b1, b2, b3 = st.columns([1, 1, 3])
                    if b1.button("Düzenle", key=f"edit_{fb['_id']}", use_container_width=True):
                        st.session_state.editing_feedback_id = str(fb['_id'])
                        st.rerun()
                    
                    if b2.button("Sil", key=f"delete_{fb['_id']}", type="secondary", use_container_width=True):
                        delete_feedback(str(fb['_id']))
                        st.rerun()

                    timestamp_dt = fb.get('timestamp', datetime.now())
                    b3.caption(f"Tarih: {timestamp_dt.strftime('%d.%m.%Y %H:%M')}")
                    
# --- Sayfayı Çalıştır ---
if __name__ == "__main__":
    feedback_page()