import streamlit as st
import base64
import os
from pathlib import Path
from core.database import get_users_collection
from bson.objectid import ObjectId

def load_css(css_file):
    """Harici CSS dosyasını yükler ve tema ayarlarını uygular."""
    try:
        with open(css_file, "r", encoding="utf-8") as f:
            css_content = f.read()
        
        # Kullanıcının tema tercihini al
        current_theme = get_user_theme()
        
        # Tema seçimine göre HTML attribute'u ayarla
        if current_theme == "Koyu Tema":
            theme_script = """
            <script>
            document.documentElement.setAttribute('data-theme', 'dark');
            </script>
            """
        else:
            theme_script = """
            <script>
            document.documentElement.removeAttribute('data-theme');
            </script>
            """
        
        # CSS ve tema script'ini uygula
        st.markdown(f"""
        <style>
        {css_content}
        </style>
        {theme_script}
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.warning(f"{css_file} bulunamadı.")

def get_user_theme():
    """Kullanıcının tema tercihini getirir. Varsayılan: Açık Tema"""
    if 'user_id' in st.session_state and st.session_state.user_id:
        try:
            users_collection = get_users_collection()
            user_id_obj = ObjectId(st.session_state.user_id)
            user = users_collection.find_one({"_id": user_id_obj})
            if user and "preferences" in user:
                return user["preferences"].get("theme", "Açık Tema")
        except Exception:
            pass
    
    # Varsayılan tema - her zaman açık tema
    return "Açık Tema"

@st.cache_data
def load_image_as_base64(file_path: str):
    """
    Bir resim dosyasını base64 string olarak yükler ve cache'ler.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            st.error(f"Logo dosyası bulunamadı: {file_path}")
            return None
        with path.open("rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Resim yüklenirken hata oluştu: {e}")
        return None

def save_user_theme(user_id, theme: str) -> bool:
    """Kullanıcının tema tercihini veritabanına kaydeder."""
    try:
        users_collection = get_users_collection()
        
        # Mevcut tema tercihini kontrol et
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        current_theme = "Açık Tema"  # Varsayılan
        if user and "preferences" in user:
            current_theme = user["preferences"].get("theme", "Açık Tema")
        
        # Eğer tema değişmemişse false döndür
        if current_theme == theme:
            return False
        
        # Tema tercihini güncelle
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"preferences.theme": theme}}
        )
        
        # Başarılı olursa session state'i işaretle
        if result.modified_count > 0:
            st.session_state.theme_changed = True
            return True
        return False
        
    except Exception as e:
        st.error(f"Tema kaydedilirken hata: {e}")
        return False

def apply_theme_to_page():
    """Sayfaya tema ayarlarını uygular - her sayfanın başında çağrılmalı"""
    # CSS dosyasını yükle ve tema ayarlarını uygula
    load_css("assets/css/style.css")
    
    # Eğer tema değişmişse sayfayı yenile
    if st.session_state.get('theme_changed', False):
        st.session_state.theme_changed = False
        st.rerun()