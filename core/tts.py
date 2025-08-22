# core/tts.py

import os
import streamlit as st
import pygame
import io
from google.cloud import texttospeech
from typing import List, Optional

@st.cache_resource
def initialize_tts_client():
    """
    Google Text-to-Speech API istemcisini başlatır ve cache'ler.
    Credentials'ın ortam değişkeni olarak ayarlandığını varsayar.
    """
    try:
        # GOOGLE_APPLICATION_CREDENTIALS ortam değişkeni .env üzerinden yüklenir.
        if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
             # .env dosyasında yolu belirtin veya doğrudan os.environ'a atayın.
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_PATH")

        return texttospeech.TextToSpeechClient()
    except Exception as e:
        st.error(f"TTS istemcisi başlatılamadı: {e}")
        return None

def list_available_voices(gender_filter: Optional[str] = None) -> List[texttospeech.Voice]:
    """
    Kullanılabilir Türkçe sesleri listeler ve cinsiyete göre filtreler.
    """
    client_tts = initialize_tts_client()
    if not client_tts:
        return []

    try:
        response = client_tts.list_voices(language_code="tr-TR")
        voices = response.voices
        
        if gender_filter:
            gender_enum = texttospeech.SsmlVoiceGender[gender_filter]
            return [voice for voice in voices if voice.ssml_gender == gender_enum]
        
        return list(voices)
    except Exception as e:
        st.error(f"Sesler listelenirken hata oluştu: {e}")
        return []

def play_audio_from_bytes(audio_content: bytes):
    """
    Verilen bytes türündeki ses içeriğini çalar.
    """
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        audio_file = io.BytesIO(audio_content)
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Sesin bitmesini bekle
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        st.error(f"Ses çalma hatası: {e}")


def play_voice_preview(voice_name: str):
    """
    Seçilen ses için kısa bir önizleme metni seslendirir ve çalar.
    """
    client_tts = initialize_tts_client()
    if not client_tts:
        st.error("Önizleme için TTS servisine bağlanılamadı.")
        return

    try:
        synthesis_input = texttospeech.SynthesisInput(text="Bu bir ses önizlemesidir.")
        voice = texttospeech.VoiceSelectionParams(language_code="tr-TR", name=voice_name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        response = client_tts.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        st.info(f"'{voice_name}' sesi için önizleme oynatılıyor...")
        play_audio_from_bytes(response.audio_content)
        st.success("Önizleme tamamlandı.")

    except Exception as e:
        st.error(f"Ses önizlemesi sırasında hata: {e}")