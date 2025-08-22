# 📚 Kitavox - Kişiselleştirilmiş Sesli Kitap Asistanı

**TÜBİTAK 2209-A Projesi**

## 🎯 Proje Hakkında

Kitavox, görme engelli bireyler başta olmak üzere geniş bir kullanıcı kitlesi için geliştirilmiş kişiselleştirilmiş sesli kitap platformudur. Google Text-to-Speech API ve yapay zeka teknolojilerini kullanarak, kullanıcılara benzersiz bir sesli okuma deneyimi sunmaktadır.

<img width="1920" height="357" alt="image" src="https://github.com/user-attachments/assets/93d1331c-87c3-4f7e-a20c-773101221d77" />
<img width="1920" height="771" alt="image" src="https://github.com/user-attachments/assets/a0038a50-ea6f-4d30-b6ce-c3482fe53a8a" />
<img width="1920" height="869" alt="image" src="https://github.com/user-attachments/assets/6f3d9d98-a2f0-4e02-a684-a160d5992c89" />

### ✨ Temel Özellikler

- 🎵 **Doğal Ses Sentezi**: Google Text-to-Speech API ile kaliteli ses çıktısı
- 🤖 **Yapay Zeka Destekli**: Kişiselleştirilmiş okuma deneyimi
- 🎨 **Kullanıcı Dostu Arayüz**: Kolay navigasyon ve kullanım
- 📱 **Çok Platform Desteği**: Farklı cihazlarda erişilebilirlik
- 🔊 **Ses Kontrolleri**: Hız, ton ve ses ayarları


## 📖 Kullanım

### Temel Kullanım

1. **Metin Yükleme**: PDF, TXT veya EPUB formatında kitapları yükleyin
2. **Ses Ayarları**: Okuma hızı, ses tonu ve volume ayarlarını yapın
3. **Dinleme**: Kişiselleştirilmiş sesli okuma deneyiminin tadını çıkarın
4. **Yer İmi**: Kaldığınız yerden devam etmek için yer imleri kullanın

### Gelişmiş Özellikler

- **Akıllı Bölümleme**: Yapay zeka ile metin bölümlerini otomatik ayırma
- **Kişiselleştirme**: Kullanıcı tercihlerine göre okuma deneyimi
- **Offline Mod**: İndirilen içerikleri çevrimdışı dinleme
- **Çoklu Dil Desteği**: Türkçe başta olmak üzere birden fazla dil

## 🏗️ Proje Yapısı

```
kitavox/
├── streamlit_app.py                 # Ana giriş noktası (kimlik doğrulama)
├── .env                            # Çevre değişkenleri
├── requirements.txt                # Python bağımlılıkları
├── style.css                       # Global CSS stilleri
│
├── pages/                          # 📄 Streamlit sayfaları
│   ├── 01_User_Profile.py         # Kullanıcı profil yönetimi
│   ├── 02_Upload_Document.py      # Belge yükleme işlemleri
│   ├── 03_Genre_Selection.py      # Tür seçimi ve tercihler
│   ├── 04_Recommended_Books.py    # AI tabanlı kitap önerileri
│   ├── 05_Listening_History.py    # Dinleme geçmişi ve istatistikler
│   ├── 06_Favorites.py            # Favori kitaplar yönetimi
│   ├── 07_Search_Books.py         # Kitap arama ve filtreleme
│   ├── 08_Book_Summary.py         # Kitap özetleri ve detayları
│   ├── 09_Ask_About_Book.py       # AI ile kitap hakkında sohbet
│   ├── 10_Feedback.py             # Kullanıcı geri bildirimleri
│   ├── 11_User_Settings.py        # Kullanıcı ayarları ve tercihler
│   └── 12_Logout.py               # Oturum kapatma işlemleri
│
├── core/                           # 🧠 Çekirdek iş mantığı
│   ├── __init__.py                # Modül başlatma dosyası
│   ├── auth.py                    # Kimlik doğrulama ve güvenlik
│   ├── database.py                # MongoDB bağlantısı ve koleksiyonlar
│   ├── tts.py                     # Text-to-Speech motor yönetimi
│   ├── gemini.py                  # Google Gemini AI entegrasyonu
│   └── recommender.py             # Öneri sistemi algoritmaları (TF-IDF, vb.)
│
├── components/                     # 🔧 Tekrar kullanılabilir UI bileşenleri
│   ├── __init__.py                # Modül başlatma dosyası
│   ├── header.py                  # Uygulama başlık bileşeni
│   ├── footer.py                  # Alt bilgi bileşeni
│   └── audio_player.py            # Ses oynatıcı ve kontrol arayüzü
│
└── utils/                          # 🛠️ Yardımcı araçlar ve fonksiyonlar
    ├── __init__.py                # Modül başlatma dosyası
    ├── helpers.py                 # Genel yardımcı fonksiyonlar
    └── ui.py                      # CSS yükleyici ve tema yönetimi
```

## 🧪 Test

```bash
# Tüm testleri çalıştır
npm test

# Test kapsamı raporu
npm run test:coverage

# E2E testler
npm run test:e2e
```

## 📊 Teknik Detaylar

### Kullanılan Teknolojiler

- **Frontend**: React.js, HTML5, CSS3
- **Backend**: Node.js, Express.js
- **API**: Google Text-to-Speech API
- **Veritabanı**: MongoDB/PostgreSQL
- **Yapay Zeka**: Custom ML models
- **Deployment**: Docker, Kubernetes

### Performans Özellikleri

- ⚡ Hızlı ses sentezi (< 2 saniye)
- 📱 Responsive tasarım
- 🔄 Real-time senkronizasyon
- 💾 Efficient caching

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak isteyenler için:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

### Kod Standartları

- ESLint ve Prettier kullanın
- Test coverage %80'in üzerinde olmalı
- Commit mesajları anlamlı olmalı
- Code review sürecine uyun

## 📝 Lisans

Bu proje [MIT License](LICENSE) altında lisanslanmıştır.

## 👥 Takım

- **Proje Sahibi**: [Elif Nur Öksüz](https://github.com/elifnuroksuzz)
- **Proje Türü**: TÜBİTAK 2209-A Araştırma Projesi

## 📞 İletişim

- 📧 E-posta: [elifnuroksuzz@email.com]
- 🐙 GitHub: [@elifnuroksuzz](https://github.com/elifnuroksuzz)
- 💼 LinkedIn: [Elif Nur Öksüz]

## 🙏 Teşekkürler

- TÜBİTAK 2209-A Programı'na destekleri için
- Google Text-to-Speech API ekibine
- Tüm beta test kullanıcılarına
- Açık kaynak topluluğuna

## 📈 Gelecek Planları

- [ ] Daha fazla dil desteği
- [ ] Gelişmiş AI özellikları
- [ ] Mobil uygulama geliştirme
- [ ] Sosyal okuma özellikleri
- [ ] Podcast entegrasyonu
- [ ] Sesli kitap pazaryeri

## 🔍 Sıkça Sorulan Sorular

**S: Kitavox ücretsiz mi?**
A: Evet, bu TÜBİTAK projesi açık kaynak ve ücretsizdir.

**S: Hangi dosya formatlarını destekliyor?**
A: PDF, TXT, EPUB ve DOCX formatlarını destekliyoruz.

**S: Çevrimdışı kullanım mümkün mü?**
A: Evet, indirilen içerikler çevrimdışı dinlenebilir.

---

**⭐ Bu proje faydalı olduysa yıldız vermeyi unutmayın!**

*Kitavox ile okuma engelleri kalkıyor, kitaplar herkese ulaşıyor! 📚🎵*
