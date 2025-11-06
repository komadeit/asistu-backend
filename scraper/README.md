# Google Maps Business Scraper

Python tabanlı Google Maps scraper. Güzellik salonları, tırnak salonları, diş klinikleri ve estetik klinikleri gibi işletmelerin verilerini Google Maps'ten çeker ve Excel dosyasına kaydeder.

## 🚀 Özellikler

- ✅ Google Maps'ten direkt veri çekme (API kullanmadan)
- ✅ Şehir ve ilçe bazlı filtreleme
- ✅ **⚡ 2-3x HIZLI:** Optimized tab-based parallelism
- ✅ **📋 İki fazlı yaklaşım:** Önce linkler, sonra detaylar
- ✅ Anti-bot önlemleri (rate limit protection)
- ✅ Excel export (DataFrame kullanarak)
- ✅ Multi-window + multi-tab desteği
- ✅ Human-like scrolling ve optimized delays

## ⚡ Performans Optimizasyonları

Bu scraper **2-3x daha hızlı** çalışır! Nasıl?

### 1. **Tab-Based Parallelism** (En büyük kazanç!)
- Tek window içinde **3 tab** paralel çalışır
- Her tab aynı anda farklı business detayını çeker
- Örnek: 60 business → Eskisi 60 sıra, Yenisi 20 batch (3x hızlı!)

### 2. **İki Fazlı Yaklaşım**
- **Faz 1:** Tüm business linklerini topla (hızlı)
- **Faz 2:** Detayları paralel çek (çok hızlı)
- Eskiden: Bul → Detay → Bul → Detay... (yavaş)
- Şimdi: Hepsini bul → Hepsinin detayını topla (hızlı)

### 3. **Optimized Delays**
- Scroll bekleme: 2s → 1s
- Request arası: 2-5s → 1-3s
- Detail page: 0.5s (çok hızlı!)
- Implicit wait: 10s → 5s

### 4. **Config'den Kontrol**
`config.py` dosyasından tüm ayarları değiştirebilirsin:
```python
NUM_WINDOWS = 2        # 2 browser window (güvenli + hızlı)
TABS_PER_WINDOW = 3    # Her window'da 3 tab paralel
DETAIL_PAGE_DELAY = 0.5  # Çok hızlı detail extraction
```

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

### 🚀 Batch Mode (Toplu Scraping) - YENİ!

Tüm kategorileri otomatik olarak tara:

```bash
# TÜM kategorileri TÜM şehirlerde tara (config.py'den)
python main.py --batch

# TÜM kategorileri tek şehirde tara
python main.py --batch --city "Istanbul"

# TÜM kategorileri İstanbul/Kadıköy'de tara
python main.py --batch --city "Istanbul" --district "Kadıköy"
```

**Batch Mode ne yapar?**
- `config.py` dosyasındaki `CATEGORIES` listesini okur
- `CITIES` listesini okur (veya --city ile override eder)
- Her kategori × şehir kombinasyonu için ayrı Excel oluşturur
- Örnek: 10 kategori × 5 şehir = **50 Excel dosyası** otomatik!

**Çıktı dosyaları:**
```
output/
├── güzellik_merkezi_Istanbul_20241105_143022.xlsx
├── güzellik_merkezi_Ankara_20241105_144530.xlsx
├── nail_salon_Istanbul_20241105_150215.xlsx
└── ...
```

### Tek Kategori Scraping

```bash
# Güzellik salonları - İstanbul (tüm ilçeler)
python main.py --category "güzellik salonu" --city "Istanbul"

# Diş klinikleri - Ankara, Çankaya
python main.py --category "diş kliniği" --city "Ankara" --district "Çankaya"

# Tırnak salonları - İzmir
python main.py --category "tırnak salonu" --city "Izmir"
```

### Parametreler

| Parametre | Zorunlu | Açıklama | Örnek |
|-----------|---------|----------|-------|
| `--batch` | ❌ Hayır | Batch mode (tüm kategorileri tara) | - |
| `--category` | ⚠️ Evet* | İşletme kategorisi (*batch yoksa zorunlu) | "güzellik salonu" |
| `--city` | ⚠️ Evet* | Şehir adı (*batch'te opsiyonel) | "Istanbul" |
| `--district` | ❌ Hayır | İlçe adı (opsiyonel) | "Kadıköy" |
| `--output` | ❌ Hayır | Özel dosya adı (batch'te göz ardı edilir) | "istanbul_salons.xlsx" |
| `--windows` | ❌ Hayır | Browser pencere sayısı (varsayılan: 2) | 3 |

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
# Browser ayarları (Optimized defaults)
NUM_WINDOWS = 2           # 2 browser window (hız/güvenlik dengesi)
TABS_PER_WINDOW = 3       # Her window'da 3 paralel tab
HEADLESS = False          # True yaparsanız browser gizli çalışır

# Anti-bot ayarları (Optimized for speed)
MIN_DELAY = 1             # Minimum bekleme (1 saniye - hızlı ama güvenli)
MAX_DELAY = 3             # Maximum bekleme (3 saniye - eskiden 5)
SCROLL_PAUSE_TIME = 1     # Scroll arası bekleme (eskiden 2)
DETAIL_PAGE_DELAY = 0.5   # Detail page çok hızlı yükleme

# Sonuç limiti
MAX_RESULTS_PER_SEARCH = 500  # Her aramada max kaç sonuç

# Batch mode kategorileri (istediğin gibi düzenle!)
CATEGORIES = [
    "güzellik merkezi",
    "güzellik salonu",
    "beauty center",
    "nail salon",
    "nail art",
    "tırnak salonu",
    "diş kliniği",
    "dental clinic",
    "estetik kliniği",
    "aesthetic clinic",
]

# Batch mode şehirleri
CITIES = [
    "Istanbul",
    "Ankara",
    "Izmir",
    "Bursa",
    "Antalya",
]
```

**Rate limit riski varsa:**
- `NUM_WINDOWS = 1` (tek window)
- `TABS_PER_WINDOW = 2` (daha az tab)
- `MIN_DELAY = 2` (daha yavaş)

## 🛡️ Anti-Bot Önlemleri

Scraper şu önlemleri alır:

1. ✅ Random user-agent rotation
2. ✅ Random delays between requests (1-3 saniye - optimized)
3. ✅ Human-like scrolling (kademeli kaydırma)
4. ✅ Non-headless mode (görünür browser)
5. ✅ WebDriver detection bypass
6. ✅ **Tab-based parallelism** (tek browser, çoklu tab - daha doğal)

**Not:** Optimizasyonlar bot-safe yapıldı!
- Default config **güvenli + hızlı** dengesi
- 2 window + 3 tab = maksimum performans, minimal risk
- Sorun olursa config'den ayarları düşür

## 🐛 Sorun Giderme

### Chrome driver hatası
Selenium 4.6+ otomatik olarak ChromeDriver'ı yönetir. Chrome tarayıcınızın güncel olduğundan emin olun.

**Windows kullanıcıları için:** İlk çalıştırmada ChromeDriver otomatik indirilir, birkaç saniye sürebilir.

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
