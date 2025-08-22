# components/header.py
import streamlit as st
from bson.objectid import ObjectId
from core.database import get_users_collection

def render_header():
    """Uygulama başlığını (header) oluşturur."""
    # CSS'in ana dosyada bir kez yüklendiğini varsayıyoruz.
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        return # Kullanıcı giriş yapmamışsa header'ı gösterme

    users_collection = get_users_collection()
    user_id_obj = ObjectId(st.session_state.user_id)
    user = users_collection.find_one({"_id": user_id_obj})
    username = user.get("username", "Kullanıcı") if user else "Kullanıcı"
    
    # Logo'nun session_state'te yüklendiğini varsayıyoruz
    logo_b64 = st.session_state.get("logo_b64")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if logo_b64:
            st.markdown(
                f'<div class="header-logo header-logo-left"><img src="data:image/jpeg;base64,{logo_b64}" alt="Kitavox Logo"></div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown('<h1 class="header-title">KITAVOX</h1>', unsafe_allow_html=True)

    with col3:
        st.markdown(
            f'<div class="header-welcome-section">'
            f'<span class="header-welcome">Hoşgeldiniz, {username}</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="header-divider">', unsafe_allow_html=True)