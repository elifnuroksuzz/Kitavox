# pages/08_Book_Summary.py

"""
Bu sayfa, kullanıcının dinleme geçmişindeki bir kitap için
yapay zeka destekli bir özet oluşturur. Kullanıcı bir kitap seçip
butona tıkladıktan sonra, kitabın detayları (kapak, yazar, kategori)
ve oluşturulan özet, düzenli bir formatta gösterilir.
"""

# -----------------------------------------------------------------------------
# Gerekli Kütüphane ve Modüllerin Import Edilmesi
# -----------------------------------------------------------------------------
import streamlit as st

# Proje içi modüllerin import edilmesi
from core.actions import get_listening_history
from core.database import get_all_books_collection
from core.gemini import initialize_gemini, get_book_summary
from components.header import render_header
from components.footer import render_footer

# -----------------------------------------------------------------------------
# Sayfa Yapılandırması ve Oturum Kontrolü
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Kitap Özeti - Kitavox",
    page_icon="📖"
)

# Oturum kontrolü
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın.")
    st.page_link("streamlit_app.py", label="Giriş Sayfasına Git", icon="🏠")
    st.stop()

# -----------------------------------------------------------------------------
# Yardımcı Fonksiyon
# -----------------------------------------------------------------------------

def prepare_history_data(user_id: str):
    """
    Kullanıcının dinleme geçmişini işleyerek her kitap için gerekli
    bilgileri (kapak, yazar vb.) içeren bir sözlük (dictionary) oluşturur.
    """
    history = get_listening_history(user_id)
    if not history:
        return {}

    all_books_collection = get_all_books_collection()
    book_data_map = {}

    for entry in history:
        book_title = entry.get("bookName", "Bilinmeyen Başlık")
        if book_title in book_data_map or book_title == "Bilinmeyen Başlık":
            continue

        is_local_file = not str(entry.get("bookUrl", "")).startswith("http")
        book_in_db = None
        
        if not is_local_file:
            book_in_db = all_books_collection.find_one({"url": entry["bookUrl"]})

        if book_in_db:
            book_data_map[book_title] = {
                "title": book_in_db.get("title", book_title),
                "cover_image": book_in_db.get("cover_image_url", "https://via.placeholder.com/120"),
                "author": book_in_db.get('author', 'Bilinmiyor'),
                "category": book_in_db.get('category', 'Bilinmiyor')
            }
        else: # Yerel dosya ise
            book_data_map[book_title] = {
                "title": book_title,
                "cover_image": "https://img.icons8.com/plasticine/100/document.png",
                "author": 'Özel Doküman',
                "category": 'Kişisel'
            }
            
    return book_data_map

# -----------------------------------------------------------------------------
# Sayfa Ana Fonksiyonu
# -----------------------------------------------------------------------------

def book_summary_page():
    """Kitap özeti sayfasının ana arayüzünü oluşturur."""
    
    render_header()
    st.title("📖 Kitap Özeti Al")

    user_id = st.session_state.user_id
    
    # 1. Adım: Dinleme geçmişini ve kitap bilgilerini arka planda hazırla
    book_data_map = prepare_history_data(user_id)

    if not book_data_map:
        st.info("Özet alabilmek için önce en az bir kitap dinlemiş olmalısınız.")
        render_footer()
        return

    # 2. Adım: Kullanıcıdan kitap seçmesini iste
    book_titles = sorted(list(book_data_map.keys()))
    selected_title = st.selectbox(
        "Hangi kitabın özetini almak istersiniz?",
        options=book_titles
    )

    # 3. Adım: "Özeti Getir" butonuna basılınca tüm işlemleri yap
    if st.button("Özeti Getir", key="get_summary_btn", type="primary"):
        if selected_title and selected_title in book_data_map:
            selected_book_data = book_data_map[selected_title]

            # --- Kitap Bilgileri Alanı ---
            st.markdown("---")
            st.subheader("Kitap Bilgileri")
            col1, col2 = st.columns([1, 3]) # Resim için 1 birim, metin için 3 birim yer ayır
            
            with col1:
                st.image(
                    selected_book_data["cover_image"], 
                    width=120 # Sabit bir genişlik vererek daha stabil bir görünüm sağlar
                )
            
            with col2:
                st.write(f"**Kitap Adı:** {selected_book_data['title']}")
                st.write(f"**Yazar:** {selected_book_data['author']}")
                st.write(f"**Kategori:** {selected_book_data['category']}")

            # --- Kitap Özeti Alanı ---
            st.markdown("---")
            st.subheader("Yapay Zeka Tarafından Oluşturulan Özet")
            
            with st.spinner(f"'{selected_title}' için özet oluşturuluyor..."):
                gemini_client = initialize_gemini()
                if not gemini_client:
                    st.error("Yapay zeka servisi şu anda kullanılamıyor.")
                else:
                    # HATA DÜZELTMESİ: Fonksiyonu, beklediği 2 argüman ile çağırıyoruz.
                    summary = get_book_summary(gemini_client, selected_title)
                    st.markdown(f"> {summary}") # Alıntı formatında göstermek için
        else:
            st.warning("Lütfen geçerli bir kitap seçin.")

    render_footer()

# --- Sayfayı Çalıştır ---
if __name__ == "__main__":
    book_summary_page()