# pages/04_⭐_Önerilen_Kitaplar.py
import streamlit as st

# Modül importları
from core.recommender import get_enhanced_recommendations
from core.actions import add_to_favorites, set_selected_book, start_listening_process
from components.header import render_header
from components.footer import render_footer



# Oturum Kontrolü
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın."); st.page_link("streamlit_app.py", label="Giriş Sayfasına Git"); st.stop()

def recommendations_page_content(user_id_str: str):
    """Sadece öneri listesini gösteren arayüz fonksiyonu."""
    render_header()
    st.title("⭐ Sizin İçin Önerilen Kitaplar")
    
    with st.spinner("Size özel öneriler hazırlanıyor..."):
        recommendations = get_enhanced_recommendations(user_id_str, n_recommendations=5)
    
    if not recommendations:
        st.warning("Size uygun bir öneri bulunamadı. Birkaç kitap dinledikten veya favorilerinize ekledikten sonra tekrar kontrol edin.")
    else:
        st.success(f"{len(recommendations)} adet kişiselleştirilmiş kitap önerisi bulundu.")
        
        for book in recommendations:
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
                if st.button("🎧 Dinle", key=f"rec_listen_{book['_id']}"):
                    set_selected_book(book, source="recommendation")
                if st.button("❤️ Favorilere Ekle", key=f"rec_fav_{book['_id']}"):
                    add_to_favorites(user_id_str, book)
    
    render_footer()

def main():
    """
    Bu sayfanın ana yönlendiricisi.
    Dinleme modunda mı yoksa normal modda mı olduğumuzu kontrol eder.
    """
    user_id = st.session_state.user_id
    
    # Eğer bir kitap dinlemek üzere seçilmişse, SADECE ses oynatıcıyı çalıştır.
    if "selected_book" in st.session_state and st.session_state.selected_book:
        start_listening_process(user_id)
    # Değilse, SADECE normal sayfa içeriğini göster.
    else:
        recommendations_page_content(user_id)

# --- Sayfayı Çalıştır ---
main()
