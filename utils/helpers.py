# utils/helpers.py
import re
from urllib.parse import unquote, urlparse
import os

def extract_book_info(url_or_path: str) -> str:
    """URL veya dosya yolundan temiz kitap adını çıkarır."""
    try:
        if url_or_path.startswith(('http://', 'https://')):
            file_path = unquote(urlparse(url_or_path).path)
            book_name = os.path.basename(file_path)
        else:
            book_name = os.path.basename(url_or_path)
        
        book_name = re.sub(r'\.pdf$', '', book_name, flags=re.IGNORECASE)
        book_name = book_name.replace('-', ' ').replace('_', ' ').title()
        return book_name.strip()
    except Exception:
        return "Bilinmeyen Kitap"

def normalize_url(url: str) -> str:
    """URL'yi karşılaştırma için standart bir formata getirir."""
    try:
        parsed = urlparse(url)
        path = unquote(parsed.path).lower()
        netloc = parsed.netloc.replace("www.", "")
        return f"{netloc}{path}"
    except Exception:
        return url

def split_text_by_bytes(text: str, max_bytes=4800) -> list[str]:
    """
    DÜZELTME: Metni, kelime kelime işleyerek UTF-8'de belirtilen byte limitini
    aşmayacak parçalara bölen daha güvenilir bir fonksiyon.
    """
    if not text:
        return []
    
    chunks = []
    current_chunk = ""
    words = text.split() # Metni kelimelere ayır

    for word in words:
        # Kelimeyi mevcut parçaya eklediğimizde limiti aşıyor mu diye kontrol et
        if len((current_chunk + " " + word).encode('utf-8')) > max_bytes:
            # Eğer aşıyorsa, mevcut parçayı listeye ekle
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Yeni parçayı bu kelimeyle başlat
            current_chunk = word
        else:
            # Limiti aşmıyorsa, kelimeyi mevcut parçaya ekle
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
    
    # Döngü bittikten sonra kalan son parçayı da listeye ekle
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks