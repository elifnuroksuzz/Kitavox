# pages/05_Listening_History.py

"""
Bu sayfa, kullanıcının dinleme geçmişini listeler.
Kullanıcılar, kaldıkları yerden dinlemeye devam edebilir,
geçmiş girdilerini silebilir veya bulunamayan yerel dosyaları
yeniden yüklemek için ilgili sayfaya yönlendirilebilir.
"""

# -----------------------------------------------------------------------------
# Gerekli Kütüphane ve Modüllerin Import Edilmesi
# -----------------------------------------------------------------------------
import streamlit as st
import os
from bson.objectid import ObjectId # MongoDB ObjectID'leri için gerekebilir

# Proje içi modüllerin import edilmesi
# Bu yollar, projenizin kök dizininden çalıştırıldığı varsayımına dayanır.
from core.database import get_all_books_collection, get_listening_history_collection
from core.actions import get_listening_history, set_selected_book
from components.header import render_header
from components.footer import render_footer
from utils.ui import load_css # CSS yükleyici (varsayımsal)

# -----------------------------------------------------------------------------
# Sayfa Yapılandırması ve Oturum Kontrolü
# -----------------------------------------------------------------------------

# Sayfa için temel yapılandırma ayarları
st.set_page_config(
    page_title="Dinleme Geçmişim - Kitavox",
    page_icon="🎧"
)

# Stil dosyasını yükle (utils/ui.py içinde böyle bir fonksiyon olduğu varsayılarak)
# load_css("style.css") 

# Oturum kontrolü: Kullanıcı giriş yapmamışsa sayfayı görüntülemesini engelle
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın.")
    # Ana giriş sayfasına yönlendirme linki
    st.page_link("streamlit_app.py", label="Giriş Sayfasına Git", icon="🏠")
    st.stop() # Sayfanın geri kalanının çalışmasını durdur

# Yüklenen dokümanlar için kalıcı dosya saklama dizini
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# -----------------------------------------------------------------------------
# Sayfa Ana Fonksiyonları
# -----------------------------------------------------------------------------

def display_listening_history():
    """Kullanıcının dinleme geçmişini arayüzde gösterir."""
    
    render_header() # components/header.py'dan gelen başlık bileşeni
    st.title("🎧 Dinleme Geçmişiniz")

    user_id = st.session_state.user_id
    history = get_listening_history(user_id)
    all_books_collection = get_all_books_collection()
    history_collection = get_listening_history_collection()

    # Dinleme geçmişi boş ise bilgilendirme mesajı göster
    if not history:
        st.info("Henüz bir dinleme geçmişiniz bulunmuyor.")
        st.page_link(
            "pages/07_Search_Books.py",
            label="Keşfetmek için Kitap Arayın",
            icon="🔍"
        )
        render_footer()
        return # Fonksiyonun devam etmesini engelle

    # Dinleme geçmişindeki her bir kayıt için döngü
    for entry in reversed(history): # Son dinleneni en üstte göstermek için
        
        is_local_file = not str(entry.get("bookUrl", "")).startswith("http")
        book_in_db = None
        
        if not is_local_file:
            book_in_db = all_books_collection.find_one({"url": entry["bookUrl"]})

        # --- Arayüz için bilgileri hazırla ---
        if book_in_db:
            # Kayıt, veritabanındaki genel bir kitaba aitse
            display_title = book_in_db.get("title", "Başlık Bilinmiyor")
            cover_image = book_in_db.get("cover_image_url", "https://via.placeholder.com/100")
            author = book_in_db.get('author', 'Bilinmiyor')
            category = book_in_db.get('category', 'Bilinmiyor')
            # Oynatıcıya gönderilecek kitap bilgisi
            book_for_player = book_in_db
        else:
            # Kayıt, kullanıcının yüklediği özel bir dokümana aitse
            display_title = entry.get("bookName", "Başlık Bilinmiyor")
            cover_image = "https://img.icons8.com/plasticine/100/document.png" # Genel doküman ikonu
            author = 'Özel Doküman'
            category = 'Kişisel'
            
            local_file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{entry['bookUrl']}")
            
            # Oynatıcıya gönderilecek kitap bilgisi (yerel dosya yolu ile)
            book_for_player = {
                "_id": entry["_id"], 
                "title": display_title, 
                "url": entry["bookUrl"], 
                "author": author, 
                "category": category,
                "is_local": True,
                "pdf_path": local_file_path if os.path.exists(local_file_path) else None
            }

        # --- İlerleme durumu bilgilerini hazırla ---
        total_pages = entry.get('pageCount', 1)
        current_page = entry.get('currentPage', 1)
        progress = min(1.0, current_page / total_pages if total_pages > 0 else 0)
        status_text = "Tamamlandı" if entry.get('isCompleted') else f"Sayfa {current_page}/{total_pages}"

        # --- Arayüzü oluştur ---
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 3, 1.2])

        with col1:
            st.image(cover_image, width=100)
        
        with col2:
            st.subheader(display_title)
            st.caption(f"Yazar: {author} | Kategori: {category}")
            st.progress(progress, text=status_text)

        with col3:
            # Eğer yerel dosya ise ve diskte bulunmuyorsa
            if is_local_file and not book_for_player["pdf_path"]:
                st.error("Bu dosya bulunamadı.", icon="🚨")
                # DOĞRU YOL KULLANIMI: Ana dizine göre tam yol verilir.
                st.page_link(
                    "pages/02_Upload_Document.py", 
                    label="Yeniden Yükle",
                    icon="🔄"
                )
            else:
                # Dosya varsa veya veritabanı kitabı ise "Devam Et" butonu
                if st.button("▶️ Devam Et", key=f"listen_{entry['_id']}", use_container_width=True):
                    # Seçilen kitabı session_state'e kaydet ve oynatma sayfasına yönlendir
                    set_selected_book(book_for_player, source="history")
                    # Oynatma sayfasına (örneğin Kitap Özet) yönlendirme
                    st.switch_page("pages/08_Book_Summary.py")

            # "Geçmişten Sil" butonu
            if st.button("🗑️ Sil", key=f"remove_{entry['_id']}", use_container_width=True):
                # Veritabanından geçmiş kaydını sil
                history_collection.delete_one({"_id": entry["_id"]})
                
                # Eğer yerel dosya ise, disktende sil
                if is_local_file and "pdf_path" in book_for_player and book_for_player["pdf_path"]:
                    if os.path.exists(book_for_player["pdf_path"]):
                        os.remove(book_for_player["pdf_path"])

                st.success(f"'{display_title}' geçmişten silindi.")
                st.rerun() # Sayfayı yenileyerek listeyi güncelle

    render_footer() # components/footer.py'dan gelen alt bilgi bileşeni

# -----------------------------------------------------------------------------
# Sayfanın Çalıştırılması
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    display_listening_history()