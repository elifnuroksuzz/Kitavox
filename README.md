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
- ♿ **Erişilebilirlik Odaklı**: Görme engelli kullanıcılar için optimize edilmiş
- 🎨 **Kullanıcı Dostu Arayüz**: Kolay navigasyon ve kullanım
- 📱 **Çok Platform Desteği**: Farklı cihazlarda erişilebilirlik
- 🔊 **Ses Kontrolleri**: Hız, ton ve ses ayarları

## 🚀 Kurulum

### Gereksinimler

```bash
# Node.js (v14 veya üstü)
# npm veya yarn
# Google Cloud Platform hesabı (TTS API için)
```

### Adım Adım Kurulum

1. **Projeyi klonlayın**
   ```bash
   git clone https://github.com/elifnuroksuzz/Kitavox.git
   cd Kitavox
   ```

2. **Bağımlılıkları yükleyin**
   ```bash
   npm install
   # veya
   yarn install
   ```

3. **Ortam değişkenlerini ayarlayın**
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyerek API anahtarlarınızı ekleyin
   ```

4. **Uygulamayı başlatın**
   ```bash
   npm start
   # veya
   yarn start
   ```

## 🔧 API Konfigürasyonu

### Google Text-to-Speech API

```javascript
// .env dosyasına ekleyin
GOOGLE_TTS_API_KEY=your_api_key_here
GOOGLE_PROJECT_ID=your_project_id
```

### Kullanım Örneği

```javascript
import { TextToSpeech } from './services/ttsService';

const tts = new TextToSpeech();
await tts.synthesizeSpeech('Merhaba, bu bir test metnidir.');
```

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
Kitavox/
├── src/
│   ├── components/        # React bileşenleri
│   ├── services/          # API servisleri
│   ├── utils/            # Yardımcı fonksiyonlar
│   ├── assets/           # Statik dosyalar
│   └── styles/           # CSS/SCSS dosyaları
├── public/               # Public dosyalar
├── docs/                 # Dökümentasyon
├── tests/                # Test dosyaları
├── .env.example         # Örnek ortam değişkenleri
├── package.json
└── README.md
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
