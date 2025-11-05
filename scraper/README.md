# Google Maps Business Scraper

Python tabanlı Google Maps scraper. Güzellik salonları, tırnak salonları, diş klinikleri ve estetik klinikleri gibi işletmelerin verilerini Google Maps'ten çeker ve Excel dosyasına kaydeder.

## 🚀 Özellikler

- ✅ Google Maps'ten direkt veri çekme (API kullanmadan)
- ✅ Şehir ve ilçe bazlı filtreleme
- ✅ Anti-bot önlemleri (rate limit protection)
- ✅ Excel export (DataFrame kullanarak)
- ✅ Multi-window desteği (paralel scraping için)
- ✅ Human-like scrolling ve delays

## 📦 Kurulum

### 1. Gereksinimler

- Python 3.8+
- Google Chrome tarayıcı

### 2. Sanal ortam oluştur (önerilen)

```bash
cd scraper
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

## 🎯 Kullanım

### Temel Kullanım

```bash
# Güzellik salonları - İstanbul (tüm ilçeler)
python main.py --category "güzellik salonu" --city "Istanbul"

# Diş klinikleri - Ankara, Çankaya
python main.py --category "diş kliniği" --city "Ankara" --district "Çankaya"

# Tırnak salonları - İzmir, Karşıyaka
python main.py --category "tırnak salonu" --city "Izmir" --district "Karşıyaka"

# Estetik klinikleri - Bursa
python main.py --category "estetik kliniği" --city "Bursa"
```

### Parametreler

| Parametre | Zorunlu | Açıklama | Örnek |
|-----------|---------|----------|-------|
| `--category` | ✅ Evet | İşletme kategorisi | "güzellik salonu" |
| `--city` | ✅ Evet | Şehir adı | "Istanbul" |
| `--district` | ❌ Hayır | İlçe adı (opsiyonel) | "Kadıköy" |
| `--output` | ❌ Hayır | Özel dosya adı | "istanbul_salons.xlsx" |
| `--windows` | ❌ Hayır | Browser pencere sayısı (varsayılan: 1) | 3 |

### Örnekler

```bash
# Özel dosya adıyla kaydet
python main.py --category "güzellik salonu" --city "Istanbul" --output "istanbul_beauty_salons.xlsx"

# 3 pencere ile paralel scraping (dikkat: rate limit riski!)
python main.py --category "diş kliniği" --city "Ankara" --windows 3
```

## 📊 Çıktı

Scraper, aşağıdaki bilgileri Excel dosyasına kaydeder:

- ✅ İşletme adı
- ✅ Kategori
- ✅ Rating (yıldız)
- ✅ Yorum sayısı
- ✅ Telefon numarası
- ✅ Adres
- ✅ Şehir
- ✅ İlçe
- ✅ Website
- ✅ Google Maps URL'i
- ✅ Arama parametreleri

Dosyalar `output/` klasörüne kaydedilir:
```
output/
├── google_maps_results_20241105_143022.xlsx
├── google_maps_results_20241105_150315.xlsx
└── ...
```

## ⚙️ Yapılandırma

`config.py` dosyasından ayarları değiştirebilirsiniz:

```python
# Browser ayarları
NUM_WINDOWS = 1          # Paralel pencere sayısı (1-4 arası önerilir)
HEADLESS = False         # True yaparsanız browser gizli çalışır

# Anti-bot ayarları
MIN_DELAY = 2           # Minimum bekleme süresi (saniye)
MAX_DELAY = 5           # Maximum bekleme süresi (saniye)

# Sonuç limiti
MAX_RESULTS_PER_SEARCH = 500  # Her aramada max kaç sonuç
```

## 🛡️ Anti-Bot Önlemleri

Scraper şu önlemleri alır:

1. ✅ Random user-agent rotation
2. ✅ Random delays between requests (2-5 saniye)
3. ✅ Human-like scrolling (kademeli kaydırma)
4. ✅ Non-headless mode (görünür browser)
5. ✅ WebDriver detection bypass

**Not:** Çok fazla istek gönderirseniz Google captcha veya rate limit uygulayabilir.
- Başlangıçta `--windows 1` ile test edin
- Sorun yoksa `--windows 3-4` deneyebilirsiniz

## 🐛 Sorun Giderme

### Chrome driver hatası
```bash
# ChromeDriver otomatik indirilmeli, ama sorun olursa:
pip install --upgrade webdriver-manager
```

### "No such element" hatası
- Google Maps'in HTML yapısı değişmiş olabilir
- Sayfalar yavaş yükleniyor olabilir
- `config.py` içinde `PAGE_LOAD_TIMEOUT` ve `IMPLICIT_WAIT` değerlerini artırın

### Rate limit / Captcha
- `NUM_WINDOWS` değerini 1'e düşürün
- `MIN_DELAY` ve `MAX_DELAY` değerlerini artırın
- Proxy kullanmayı düşünün

## 📝 Notlar

- Scraper Google Maps'in Türkçe arayüzü ile test edilmiştir
- İngilizce arayüzde bazı selector'lar farklı olabilir
- Büyük veri setleri için scraping uzun sürebilir (100 işletme ~10-15 dakika)
- Etik kullanım: Sadece kendi işiniz için kullanın, spam yapmayın

## 📄 Lisans

Bu proje açık kaynaklıdır ve eğitim amaçlıdır.
