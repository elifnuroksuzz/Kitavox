# pages/01_User_Profile.py
import streamlit as st
import pandas as pd
import plotly.express as px
import bcrypt
from PIL import Image
from io import BytesIO
import base64
from bson.objectid import ObjectId





# Modüler yapıdaki importlar
from core.database import (
    get_users_collection,
    get_listening_history_collection,
    get_favorites_collection,
    get_feedback_collection,
    get_all_books_collection  # Bu import eksikti, eklendi.
)

# --- Oturum Kontrolü ---
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    # Ana sayfaya yönlendir (streamlit_app.py)
    st.switch_page("streamlit_app.py")

# Mongo koleksiyonlarını al
users_collection = get_users_collection()
listening_history_collection = get_listening_history_collection()
favorites_collection = get_favorites_collection()
feedback_collection = get_feedback_collection()
all_books_collection = get_all_books_collection()

# --- PROFİL İÇİN YARDIMCI FONKSİYONLAR (GÜNCELLENMİŞ) ---

def get_user_preferences(user_id_obj):
    # DÜZELTME: Bu fonksiyon artık all_books_collection'ı kullanarak tercihleri doğru bir şekilde analiz ediyor.
    preferences = {"categories": {}, "authors": {}, "read_books": set()}
    history = list(listening_history_collection.find({"userId": user_id_obj}))
    
    for entry in history:
        book_url = entry.get("bookUrl")
        preferences["read_books"].add(book_url)
        
        book = all_books_collection.find_one({"url": book_url})
        if book:
            if book.get("category"):
                cat = book["category"]
                preferences["categories"][cat] = preferences["categories"].get(cat, 0) + 1
            if book.get("author"):
                author = book["author"]
                preferences["authors"][author] = preferences["authors"].get(author, 0) + 1
                
    return preferences

def create_user_profile(user_id_obj):
    history = list(listening_history_collection.find({"userId": user_id_obj}))
    favorites = list(favorites_collection.find({"userId": user_id_obj}))
    
    return {
        "completed_books": [h["bookUrl"] for h in history if h.get("isCompleted")],
        "incomplete_books": [h["bookUrl"] for h in history if not h.get("isCompleted")],
        "favorite_books": [f["bookUrl"] for f in favorites],
    }

def create_detailed_user_profile(user_id_str):
    user_id_obj = ObjectId(user_id_str)
    user = users_collection.find_one({"_id": user_id_obj})
    if not user:
        return None

    basic_profile = create_user_profile(user_id_obj)
    preferences = get_user_preferences(user_id_obj)
    
    # DÜZELTME: Gün dağılımı ve tercihler artık veritabanından dinamik olarak geliyor.
    history = list(listening_history_collection.find({"userId": user_id_obj}))
    day_distribution = {}
    day_mapping = {"Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba", "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"}
    for entry in history:
        if "timestamp" in entry:
            day_en = entry["timestamp"].strftime("%A")
            day_tr = day_mapping.get(day_en, day_en)
            day_distribution[day_tr] = day_distribution.get(day_tr, 0) + 1

    profile = {
        "user_id": user_id_str,
        "username": user.get("username", "Bilinmeyen"),
        "profile_photo": user.get("profile_photo", None),
        "bio": user.get("bio", ""),
        "completed_books_count": len(basic_profile.get("completed_books", [])),
        "incomplete_books_count": len(basic_profile.get("incomplete_books", [])),
        "favorites_count": len(basic_profile.get("favorite_books", [])),
        "preferred_categories": sorted(preferences["categories"].items(), key=lambda x: x[1], reverse=True)[:5],
        "preferred_authors": sorted(preferences["authors"].items(), key=lambda x: x[1], reverse=True)[:5],
        "day_distribution": sorted(day_distribution.items(), key=lambda x: x[1], reverse=True),
    }
    return profile

def change_password(user_id_str):
    user_id_obj = ObjectId(user_id_str)
    st.subheader("Şifre Değiştir")
    with st.form(key="password_change_form"):
        current_password = st.text_input("Mevcut Şifre", type="password")
        new_password = st.text_input("Yeni Şifre", type="password")
        confirm_password = st.text_input("Yeni Şifreyi Onayla", type="password")
        submit_button = st.form_submit_button("Şifreyi Değiştir")

        if submit_button:
            user = users_collection.find_one({"_id": user_id_obj})
            if not user:
                st.error("Kullanıcı bulunamadı."); return
            if not bcrypt.checkpw(current_password.encode("utf-8"), user.get("password")):
                st.error("Mevcut şifreniz yanlış."); return
            if len(new_password) < 8:
                st.error("Yeni şifre en az 8 karakter olmalıdır."); return
            if new_password != confirm_password:
                st.error("Yeni şifreler eşleşmiyor."); return
            new_hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            users_collection.update_one({"_id": user_id_obj}, {"$set": {"password": new_hashed_pw}})
            st.success("Şifreniz başarıyla değiştirildi!")
            st.session_state.editing_mode = None
            st.rerun()

def show_profile_edit_form(user_id_str):
    user_id_obj = ObjectId(user_id_str)
    st.subheader("Profil Bilgilerini Düzenle")
    user = users_collection.find_one({"_id": user_id_obj})
    if not user:
        st.error("Kullanıcı bilgileri bulunamadı."); return

    with st.form(key="profile_edit_form"):
        username = st.text_input("Kullanıcı Adı", value=user.get("username", ""))
        bio = st.text_area("Hakkımda", value=user.get("bio", ""), height=100)
        uploaded_file = st.file_uploader("Yeni bir profil fotoğrafı yükle", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("Değişiklikleri Kaydet")
        if submit_button:
            update_fields = {"username": username, "bio": bio}
            if uploaded_file is not None:
                try:
                    image = Image.open(uploaded_file)
                    image.thumbnail((200, 200))
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    update_fields["profile_photo"] = f"data:image/png;base64,{img_str}"
                except Exception as e:
                    st.error(f"Resim işlenirken hata oluştu: {e}")
            users_collection.update_one({"_id": user_id_obj}, {"$set": update_fields})
            st.success("Profil başarıyla güncellendi!")
            st.session_state.editing_mode = None
            st.rerun()

# --- ANA GÖRÜNTÜLEME FONKSİYONU (TÜRKÇELEŞTİRİLMİŞ) ---
def display_user_profile(user_id_str):
    profile = create_detailed_user_profile(user_id_str)
    if not profile:
        st.error("Kullanıcı profili oluşturulamadı.")
        return

    col1, col2 = st.columns([1, 3])
    with col1:
        if profile.get("profile_photo"):
            st.image(profile["profile_photo"], width=150, caption="Profil Resmi")
        else:
            st.image("https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg", width=150)

    with col2:
        st.header(f"Hoş Geldiniz, {profile.get('username', 'Kullanıcı')}")
        st.write(f"**Hakkımda:** {profile.get('bio', 'Belirtilmemiş.')}")

    st.markdown("---")

    if 'editing_mode' not in st.session_state:
        st.session_state.editing_mode = None

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    if btn_col1.button("Profili Düzenle"):
        st.session_state.editing_mode = "profile"
    if btn_col2.button("Şifre Değiştir"):
        st.session_state.editing_mode = "password"
    if st.session_state.editing_mode and btn_col3.button("İptal"):
        st.session_state.editing_mode = None
        st.rerun()

    if st.session_state.editing_mode == "profile":
        show_profile_edit_form(user_id_str)
    elif st.session_state.editing_mode == "password":
        change_password(user_id_str)
    
    st.markdown("---")

    st.subheader("İstatistikleriniz")
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.metric("Tamamlanan Kitap", profile.get('completed_books_count', 0))
    stat_col2.metric("Devam Eden Kitap", profile.get('incomplete_books_count', 0))
    stat_col3.metric("Favori Kitap", profile.get('favorites_count', 0))

    st.markdown("---")

    st.subheader("Dinleme Alışkanlıklarınız")
    day_dist = profile.get("day_distribution")
    if day_dist:
        df_days = pd.DataFrame(day_dist, columns=["Gün", "Oturum Sayısı"])
        fig = px.bar(df_days, x="Gün", y="Oturum Sayısı", title="Günlere Göre Dinleme Dağılımı")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Grafik oluşturmak için dinleme geçmişi bulunamadı.")

# === SAYFAYI ÇALIŞTIRAN ANA KOD ===
st.set_page_config(page_title="Kullanıcı Profili", layout="wide")
st.title("👤 Kullanıcı Profilim")

display_user_profile(st.session_state.user_id)