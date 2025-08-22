# components/audio_player.py
import streamlit as st
import pygame
import io
import time
import hashlib
from google.cloud import texttospeech
from core.tts import initialize_tts_client

# Bu fonksiyon, actions modülü tarafından dinamik olarak atanacak.
# Bu, modüller arası döngüsel bağımlılığı (circular import) önler.
dinleme_gecmisi_ekle = lambda *args, **kwargs: None

def audio_player_component(
    pages: list[str],
    user_preferences: dict,
    user_id: str,
    kitap_url: str,
    start_page: int, # 0-indexed
    physical_pages_total: int,
    book_name: str
):
    st.header(f"🎧 Dinleniyor: {book_name}")
    
    session_key = f"audio_player_{hashlib.md5(f'{user_id}_{kitap_url}'.encode()).hexdigest()[:10]}"

    if session_key not in st.session_state:
        st.session_state[session_key] = {
            'current_page_index': start_page,
            'is_playing': False,
            'is_paused': False,
            'audio_data': None,
            'last_played_time': 0,
        }
    
    player_state = st.session_state[session_key]

    client_tts = initialize_tts_client()
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            st.error("Ses donanımı başlatılamadı. Lütfen tarayıcınızın sesi kullanmasına izin verdiğinizden emin olun.")
            return

    def play_current_page():
        page_index = player_state['current_page_index']
        if page_index >= len(pages):
            st.success("Kitap tamamlandı!")
            player_state['is_playing'] = False
            return

        page_text = pages[page_index].strip()
        if not page_text:
            player_state['current_page_index'] += 1
            play_current_page()
            return
        
        with st.spinner(f"Sayfa {page_index + 1} seslendiriliyor..."):
            synthesis_input = texttospeech.SynthesisInput(text=page_text)
            voice_gender_str = user_preferences.get("voice_gender", "FEMALE")
            voice = texttospeech.VoiceSelectionParams(
                language_code="tr-TR",
                name=user_preferences.get("voice_name"),
                ssml_gender=texttospeech.SsmlVoiceGender[voice_gender_str]
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=user_preferences.get("speaking_rate"),
                pitch=user_preferences.get("pitch")
            )
            response = client_tts.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            player_state['audio_data'] = response.audio_content
        
        audio_file = io.BytesIO(player_state['audio_data'])
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        player_state['is_playing'] = True
        player_state['is_paused'] = False
        player_state['last_played_time'] = time.time()
        dinleme_gecmisi_ekle(user_id, kitap_url, physical_pages_total, current_page=page_index + 1)

    progress = (player_state['current_page_index'] + 1) / physical_pages_total if physical_pages_total > 0 else 0
    st.progress(progress, text=f"Sayfa {player_state['current_page_index'] + 1} / {physical_pages_total}")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    # DÜZELTME: Her butona session_key kullanarak benzersiz bir 'key' eklendi.
    if c1.button("⏮️ Önceki", disabled=player_state['current_page_index'] == 0, key=f"{session_key}_prev"):
        pygame.mixer.music.stop()
        player_state['current_page_index'] -= 1
        play_current_page()
        st.rerun()

    if player_state['is_playing'] and not player_state['is_paused']:
        if c2.button("⏸️ Duraklat", key=f"{session_key}_pause"):
            pygame.mixer.music.pause()
            player_state['is_paused'] = True
            st.rerun()
    else:
        if c2.button("▶️ Oynat", type="primary", key=f"{session_key}_play"):
            if player_state['is_paused']:
                pygame.mixer.music.unpause()
                player_state['is_paused'] = False
            else:
                play_current_page()
            st.rerun()

    if c3.button("⏭️ Sonraki", disabled=player_state['current_page_index'] >= len(pages) - 1, key=f"{session_key}_next"):
        pygame.mixer.music.stop()
        player_state['current_page_index'] += 1
        play_current_page()
        st.rerun()
        
    if c5.button("⏹️ Bitir", key=f"{session_key}_stop"):
        pygame.mixer.music.stop()
        dinleme_gecmisi_ekle(user_id, kitap_url, physical_pages_total, current_page=player_state['current_page_index'] + 1)
        st.session_state.pop('selected_book', None)
        st.session_state.pop(session_key, None)
        st.success("Dinleme sonlandırıldı.")
        st.rerun()

    if player_state['is_playing'] and not player_state['is_paused'] and not pygame.mixer.music.get_busy():
        if time.time() - player_state.get('last_played_time', 0) > 1.0:
            if player_state['current_page_index'] < len(pages) - 1:
                player_state['current_page_index'] += 1
                play_current_page()
                st.rerun()
            else:
                player_state['is_playing'] = False
                dinleme_gecmisi_ekle(user_id, kitap_url, physical_pages_total, current_page=physical_pages_total)
                st.success("Kitap başarıyla tamamlandı!")
                st.rerun()
