# core/auth.py
import streamlit as st
import bcrypt
from datetime import datetime, timezone
from core.database import get_users_collection

# (hash_password, verify_password, validate_password fonksiyonları aynı kalır)
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    if not isinstance(hashed_password, bytes): return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)

def validate_password(password: str) -> bool:
    return (
        len(password) >= 8 and
        any(c.isdigit() for c in password) and
        any(c.isupper() for c in password) and
        any(c.islower() for c in password)
    )

def login_page():
    users_collection = get_users_collection()
    st.header("Giriş Yap")
    with st.form(key="login_form"):
        email = st.text_input("E-posta Adresi")
        password = st.text_input("Şifre", type="password")
        submit_button = st.form_submit_button(label='Giriş Yap')

        if submit_button:
            if users_collection is None:
                st.error("Veritabanı bağlantısı mevcut değil.")
                return

            user = users_collection.find_one({"email": email})
            if user and 'password' in user and verify_password(password, user["password"]):
                st.session_state.user_id = str(user["_id"])
                st.session_state.username = user.get("username", "Kullanıcı")
                st.rerun()
            else:
                st.error("Geçersiz e-posta veya şifre.")

def register_page():
    users_collection = get_users_collection()
    st.header("Kayıt Ol")
    with st.form(key="register_form"):
        username = st.text_input("Kullanıcı Adı")
        email = st.text_input("E-posta Adresi")
        password = st.text_input("Şifre", type="password")
        submit_button = st.form_submit_button(label='Kayıt Ol')

        if submit_button:
            if users_collection is None:
                st.error("Veritabanı bağlantısı mevcut değil.")
                return
            if not validate_password(password):
                st.warning("Şifre en az 8 karakter olmalı, büyük/küçük harf ve rakam içermelidir.")
                return
            if users_collection.find_one({"email": email}):
                st.warning("Bu e-posta adresi zaten kayıtlı.")
                return

            user_doc = {
                "username": username,
                "email": email,
                "password": hash_password(password),
                "createdAt": datetime.now(timezone.utc),
                "preferences": {"voice_gender": "FEMALE", "speaking_rate": 1.0, "pitch": 0.0, "theme": "Açık Tema"},
            }
            users_collection.insert_one(user_doc)
            st.success("Kayıt başarılı. Şimdi giriş yapabilirsiniz.")