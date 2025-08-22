# pages/11_User_Settings.py
import streamlit as st
from bson.objectid import ObjectId
from core.database import get_users_collection
from core.tts import list_available_voices, play_voice_preview

if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Bu sayfayı görüntülemek için lütfen giriş yapın.")
    st.page_link("streamlit_app.py", label="Giriş Sayfasına Git")
    st.stop()

def handle_user_settings(user_id_str: str):
    st.title("Kullanıcı Ayarları")
    users_collection = get_users_collection()
    user_id_obj = ObjectId(user_id_str)
    user = users_collection.find_one({"_id": user_id_obj})
    
    if not user:
        st.error("Kullanıcı bulunamadı.")
        return
    
    current_prefs = user.get("preferences", {})

    with st.expander("Ses Ayarları", expanded=True):
        st.subheader("Tercih Ettiğiniz Sesi Seçin")
        gender_map = {"Kadın": "FEMALE", "Erkek": "MALE"}
        current_gender_name = "Kadın" if current_prefs.get("voice_gender") == "FEMALE" else "Erkek"
        gender_choice_name = st.radio("Ses Cinsiyeti", options=["Kadın", "Erkek"], 
                                    index=["Kadın", "Erkek"].index(current_gender_name), horizontal=True)
        gender_choice_code = gender_map[gender_choice_name]

        voices = list_available_voices(gender_filter=gender_choice_code)
        if voices:
            voice_options = {v.name: f"{v.name} - ({v.ssml_gender.name.capitalize()})" for v in voices}
            current_voice_name = current_prefs.get("voice_name")
            try:
                default_index = list(voice_options.keys()).index(current_voice_name)
            except ValueError:
                default_index = 0

            selected_voice_name = st.selectbox("Mevcut Sesler", options=voice_options.keys(), 
                                             format_func=lambda name: voice_options[name], index=default_index)
            col1, col2 = st.columns([1, 3])
            if col1.button("Sesi Önizle"):
                play_voice_preview(selected_voice_name)

        st.subheader("Konuşma Hızını ve Tonunu Ayarlayın")
        speaking_rate = st.slider("Konuşma Hızı", min_value=0.5, max_value=2.0, 
                                value=current_prefs.get("speaking_rate", 1.0), step=0.05)
        pitch = st.slider("Ses Tonu", min_value=-10.0, max_value=10.0, 
                        value=current_prefs.get("pitch", 0.0), step=0.5)

        if st.button("Ses Ayarlarını Kaydet"):
            new_prefs = {
                "voice_gender": gender_choice_code,
                "voice_name": selected_voice_name,
                "speaking_rate": speaking_rate,
                "pitch": pitch
            }
            users_collection.update_one({"_id": user_id_obj}, 
                                      {"$set": {f"preferences.{k}": v for k, v in new_prefs.items()}})
            st.success("Ses ayarları başarıyla kaydedildi!")
            st.rerun()

    st.markdown("---")

    with st.expander("Tema Ayarları", expanded=True):
        st.subheader("Uygulama Temasını Seçin")
        current_theme = current_prefs.get("theme", "Açık Tema")
        theme_choice = st.radio("Tema", options=["Açık Tema", "Koyu Tema"], 
                              index=0 if current_theme == "Açık Tema" else 1, horizontal=True)

        if st.button("Temayı Kaydet"):
            if save_user_theme(user_id_obj, theme_choice):
                st.success("Tema kaydedildi! Sayfa yenileniyor...")
                # Tema değişikliği için sayfayı yenile
                st.rerun()
            else:
                st.info("Tema zaten bu seçenekte ayarlı.")

handle_user_settings(st.session_state.user_id)