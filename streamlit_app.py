# streamlit_app.py

import streamlit as st
import os
from core.auth import login_page, register_page
from utils.ui import load_css, load_image_as_base64

st.set_page_config(
    page_title="Kitavox Giriş", 
    page_icon="📚", 
    layout="wide"
)

# --- Oturum Yönetimi ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = "Kullanıcı"

# --- YARDIMCI FONKSİYON ---
def get_first_page():
    """'pages' klasöründeki ilk sayfayı (alfabetik olarak) bulur."""
    pages_dir = "pages"
    if os.path.exists(pages_dir) and os.path.isdir(pages_dir):
        pages = sorted([f for f in os.listdir(pages_dir) if f.endswith(".py")])
        if pages:
            return os.path.join(pages_dir, pages[0])
    return None

# --- Ana Akış ---
def main():
    if st.session_state.user_id:
        # Kullanıcı giriş yapmışsa, doğrudan ilk sayfaya yönlendir.
        first_page = get_first_page()
        if first_page:
            st.switch_page(first_page)
        else:
            st.error("Uygulama sayfaları bulunamadı.")
            st.stop()
    else:
        # DÜZELTME: Kullanıcı giriş yapmamışsa, kenar çubuğunu CSS ile gizle.
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Ana ekranda giriş/kayıt sekmelerini göster.
        st.title("Kitavox'a Hoş Geldiniz")
        st.info("Lütfen devam etmek için giriş yapın veya yeni bir hesap oluşturun.")

        login_tab, register_tab = st.tabs(["Giriş Yap", "Kayıt Ol"])

        with login_tab:
            login_page()

        with register_tab:
            register_page()

if __name__ == "__main__":
    main()
