# pages/09_Ask_About_Book.py

"""
Bu sayfa, kullanıcının dinleme geçmişindeki bir kitap hakkında
yapay zekaya sorular sormasını sağlar. Kullanıcı bir kitap seçtiğinde,
kitabın detayları gösterilir ve altında bir soru formu belirir.
"""

# -----------------------------------------------------------------------------
# Gerekli Kütüphane ve Modüllerin Import Edilmesi
# -----------------------------------------------------------------------------
import streamlit as st

# Proje içi modüllerin import edilmesi
from core.actions import get_listening_history
from core.database import get_all_books_collection
from core.gemini import initialize_gemini, answer_book_question
from components.header import render_header
from components.footer import render_footer

# -----------------------------------------------------------------------------
# Sayfa Yapılandırması ve Oturum Kontrolü
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Kitaba Soru Sor - Kitavox",
    page_icon="❓"
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

def ask_about_book_page():
    """Kitap hakkında soru sorma sayfasının ana arayüzünü oluşturur."""
    
    render_header()
    st.title("❓ Kitap Hakkında Soru Sor")
    st.markdown("Dinleme geçmişinizdeki bir kitap hakkında merak ettiklerinizi yapay zekaya sorun.")

    user_id = st.session_state.user_id
    
    # 1. Adım: Verileri arka planda hazırla
    book_data_map = prepare_history_data(user_id)

    if not book_data_map:
        st.info("Soru sorabilmek için önce en az bir kitap dinlemiş olmalısınız.")
        st.page_link("pages/07_Search_Books.py", label="Kitapları Keşfet", icon="🔍")
        render_footer()
        return

    # 2. Adım: Kullanıcıdan kitap seçmesini iste
    book_titles = ["Lütfen bir kitap seçin..."] + sorted(list(book_data_map.keys()))
    selected_title = st.selectbox(
        "Hangi kitap hakkında soru sormak istersiniz?",
        options=book_titles,
        index=0
    )

    # 3. Adım: Kitap seçildiyse, detayları ve soru formunu göster
    if selected_title != "Lütfen bir kitap seçin...":
        selected_book_data = book_data_map[selected_title]
        author = selected_book_data.get('author', 'Bilinmiyor')
        
        # --- Kitap Bilgileri Alanı (İstenen Tasarım) ---
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(selected_book_data["cover_image"], width=120)
        
        with col2:
            st.subheader(selected_book_data['title'])
            st.caption(f"**Yazar:** {author} | **Kategori:** {selected_book_data['category']}")

        st.markdown("---")

        # --- Soru Sorma Formu ---
        with st.form("question_form"):
            question = st.text_area("Sorunuzu buraya yazın:", placeholder="Örn: Kitabın ana teması nedir?")
            submitted = st.form_submit_button("Cevap Al", type="primary")

            if submitted and question:
                gemini_client = initialize_gemini()
                if not gemini_client:
                    st.error("Yapay zeka servisi şu anda kullanılamıyor.")
                else:
                    with st.spinner("Yapay zeka yanıtınızı hazırlıyor..."):
                        answer = answer_book_question(gemini_client, selected_title, author, question)
                        st.subheader("Yapay Zeka Yanıtı")
                        st.markdown(answer)

    render_footer()

# --- Sayfayı Çalıştır ---
if __name__ == "__main__":
    ask_about_book_page()