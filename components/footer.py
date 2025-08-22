# components/footer.py
import streamlit as st
from datetime import datetime
import pytz

# Türkiye saat dilimini ayarla
TR_TZ = pytz.timezone("Europe/Istanbul")

def render_footer():
    """Uygulama altbilgisini (footer) oluşturur."""
    st.markdown('<hr class="footer-divider">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="footer-section">
                <h3>Kitavox</h3>
                <p>Kişiselleştirilmiş sesli kitap deneyimiyle bilgiye ulaşın.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="footer-section">
                <h3>İletişim</h3>
                <p>linkedin.com/in/elifnuroksuz</p>
                <p>github.com/elifnuroksuz</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="footer-section">
                <h3>Bizi Takip Edin</h3>
                <p>Sosyal medya linkleri buraya eklenebilir.</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown(
        f"""
        <div class="footer-copyright">
            © {datetime.now(TR_TZ).year} Kitavox. Tüm hakları saklıdır.
        </div>
        """,
        unsafe_allow_html=True,
    )