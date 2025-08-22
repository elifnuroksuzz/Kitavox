# utils/data_processing.py
import streamlit as st
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import tempfile
import os
import re
from urllib.parse import urljoin

BASE_URL = "https://dijitalkitaplar.net"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
SESSION = requests.Session()

def fetch_page(path):
    try:
        full_url = urljoin(BASE_URL, path)
        response = SESSION.get(full_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        st.error(f"Sayfa alınamadı: {e}")
        return None

def download_and_process_pdf(pdf_kaynak: str) -> tuple[list[str], int]:
    """
    PDF'i indirir veya yerel dosyayı açar ve metin içeriğini çıkarır.
    DÜZELTME: Metin çıkarma yöntemi, karmaşık ve taranmış PDF'lerle başa çıkmak için iyileştirildi.
    """
    temp_file_path = None
    try:
        is_url = pdf_kaynak.startswith(('http://', 'https://'))
        if is_url:
            response = requests.get(pdf_kaynak, headers=HEADERS, timeout=30)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            pdf_path = temp_file_path
        else:
            pdf_path = pdf_kaynak

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")

        doc = fitz.open(pdf_path)
        pages_text = []
        for page_num, page in enumerate(doc):
            # DÜZELTME: Metni daha akıllıca çıkarmak için "dict" formatını kullanıyoruz.
            # Bu, metnin konumunu ve yapısını daha iyi analiz etmemizi sağlar.
            page_dict = page.get_text("dict", sort=True)
            page_content = []
            
            for block in page_dict.get("blocks", []):
                if block['type'] == 0: # Metin bloklarını işle
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        page_content.append(line_text.strip())
            
            # DÜZELTME: Satır sonlarındaki tireleri birleştirerek kelimelerin bölünmesini engelle
            full_page_text = " ".join(page_content)
            full_page_text = re.sub(r'-\s+', '', full_page_text)
            
            # DÜZELTME: Anlamsız karakterleri ve gereksiz boşlukları temizle
            cleaned_text = re.sub(r'\s+', ' ', full_page_text).strip()
            
            # Sadece anlamlı metin içeren sayfaları ekle
            if cleaned_text and len(cleaned_text) > 10: # Çok kısa veya boş sayfaları atla
                 pages_text.append(cleaned_text)

        physical_pages = doc.page_count
        doc.close()
        return pages_text, physical_pages
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def extract_text_from_html(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        st.error(f"HTML metni okunurken hata: {e}")
        return ""
