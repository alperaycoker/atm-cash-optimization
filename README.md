# 🏧 ATM Nakit Akış Optimizasyonu (Cash Flow Optimization)

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Model](https://img.shields.io/badge/Model-XGBoost-orange)
![Deployment](https://img.shields.io/badge/Deployment-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://atm-cash-optimization-alperay.streamlit.app/)

> **🔴 Canlı Demo:** Projeyi tarayıcınızda denemek için [buraya tıklayın](https://atm-cash-optimization-alperay.streamlit.app/).

## 📸 Uygulama Önizleme
> *Geliştirilen yapay zeka destekli karar destek sisteminin arayüzü:*

![Uygulama Ekran Görüntüsü](app_screenshot.png)

---

## 📌 Yönetici Özeti (Executive Summary)
Bu proje, bankacılık sektöründe en kritik operasyonel maliyet kalemlerinden biri olan **ATM Nakit Yönetimi** problemini çözmek amacıyla geliştirilmiştir. Gelişmiş makine öğrenmesi (Time Series Forecasting) teknikleri kullanılarak, her bir ATM'nin nakit ihtiyacı saatlik bazda %95 güven aralığı ile tahmin edilmektedir.

**Çözülen İş Problemleri:**
1.  **Atıl Nakit (Idle Cash):** ATM'lerde ihtiyaç fazlası bekleyen paranın yarattığı faiz/fırsat maliyetini minimize etmek.
2.  **Operasyonel Risk (Stockout):** Nakdin beklenmedik şekilde tükenmesi sonucu oluşan müşteri memnuniyetsizliği ve acil ikmal (CIT) maliyetlerini önlemek.

**Hedeflenen Etki:**
Model simülasyonlarına göre, geleneksel "sabit yükleme" yöntemine kıyasla bankanın nakit operasyon maliyetlerinde **%15-%20 arasında tasarruf** sağlanmaktadır.

---

## 🚀 Temel Özellikler
Proje, sadece bir modelleme çalışması değil, uçtan uca bir **MLOps** döngüsü olarak tasarlanmıştır:

* **🤖 Uçtan Uca ML Pipeline:** `src/pipeline.py` scripti ile veri okuma, temizleme, özellik mühendisliği (Feature Engineering), model eğitimi ve sürümleme süreçleri tam otomatize edilmiştir.
* **⚠️ Drift Detection (Veri Kayması Tespiti):** Kullanıcı, modelin eğitim dağılımının dışında (anormal) bir değer girdiğinde sistem otomatik olarak güven uyarısı verir.
* **📊 Canlı Monitoring:** Yapılan tüm tahminler, girdi parametreleri ve hesaplanan finansal tasarruf miktarı `monitoring.db` (SQLite) veritabanında loglanır ve arayüzde raporlanır.
* **🧠 XAI (Açıklanabilir Yapay Zeka):** SHAP (SHapley Additive exPlanations) analizi entegrasyonu ile modelin kararlarının şeffaflığı sağlanmıştır (Örn: "Dün çekilen para miktarı tahmini %40 artırdı").
* **💰 Business Logic & Simülasyon:** Model çıktılarına dinamik "Güvenlik Marjı" (Safety Margin) eklenerek operasyonel risk minimize edilir ve finansal kâr/zarar analizi gerçek zamanlı sunulur.

---

## 📂 Proje Yapısı (Repository Structure)
Profesyonel yazılım geliştirme standartlarına uygun modüler yapı:

```text
atm-project/
├── data/                  # Ham ve İşlenmiş Veri Setleri
├── models/                # Eğitilmiş Model Dosyaları (.json)
├── notebooks/             # Deneysel Çalışmalar & Raporlama
│   ├── 1_eda.ipynb        # Keşifçi Veri Analizi
│   ├── 2_baseline.ipynb   # Baseline Model Kurulumu
│   ├── 3_feature_eng.ipynb# Özellik Çıkarımı (Lags, Rolling Windows)
│   ├── 4_optimization.ipynb # Hiperparametre Optimizasyonu
│   └── 5_evaluation.ipynb # SHAP ve Model Değerlendirme
├── src/                   # Prodüksiyon Kodları
│   ├── config.py          # Merkezi Ayar ve Konfigürasyon Dosyası
│   ├── inference.py       # Profesyonel Tahmin Motoru Sınıfı
│   └── pipeline.py        # Pipeline Otomasyon Scripti
├── app.py                 # Streamlit Web Arayüzü
├── Dockerfile             # Docker Konteyner Dosyası
├── requirements.txt       # Proje Bağımlılıkları
└── README.md              # Proje Dokümantasyonu

```

## 📝 Proje Raporu & Teknik Detaylar
*(ML Bootcamp Değerlendirme Kriterlerine İstinaden)*

### 1) Problem Tanımı
ATM ağındaki nakit talebinin zaman serisi analizi ile tahmin edilmesi ve "Atıl Nakit" (Idle Cash) ile "Operasyonel Risk" (Stockout) maliyetlerinin minimize edilmesi hedeflenmiştir.

### 2) Baseline Süreci ve Skoru
Projenin başlangıcında herhangi bir optimizasyon yapılmadan, varsayılan parametrelerle bir **XGBoost Regressor** eğitilmiştir. Bu "ham" modelin performans metriği olarak **MAE: ~750 TL** (Ortalama Mutlak Hata) seviyeleri gözlemlenmiştir. Bu skor, model iyileştirmeleri için referans noktası kabul edilmiştir.

### 3) Feature Engineering Denemeleri
Zaman serisi desenlerini yakalamak için üç ana kategoride özellik üretilmiştir:
* **Lag Features:** Geçmiş saatlerdeki çekimler (`lag_1`, `lag_24`). Sonuç: Model başarısını en çok artıran özellikler oldu.
* **Rolling Windows:** Hareketli ortalamalar (`rolling_mean_3`, `rolling_mean_24`). Sonuç: Trendi yakalamada etkili oldu.
* **Takvimsel:** `hour`, `is_weekend`. Sonuç: Hafta sonu ve mesai saati dalgalanmalarını modelledi.

### 4) Validasyon Şeması ve Nedeni
Veri seti zaman serisi (Time Series) yapısında olduğu için rastgele karıştırma (Random Shuffle) yerine **Time Series Split** yöntemi tercih edilmiştir.
* **Neden:** Gelecekteki verinin (yarın), geçmişi (dünü) eğitmesini engellemek (Data Leakage) ve modelin gerçek hayat senaryosuna uygun olarak "geçmişten öğrenip geleceği tahmin etmesini" sağlamak için kronolojik ayrım yapılmıştır (%80 Eğitim - %20 Test).

### 5) Final Pipeline ve Feature Seçimi
Final modelde kullanılacak özellikler rastgele değil, **SHAP (SHapley Additive exPlanations)** analizine göre seçilmiştir.
* **Strateji:** SHAP değerlerine göre modele katkısı düşük olan veya gürültü yaratan özellikler elenmiş; `lag_24` ve `hour` gibi yüksek etki gücüne sahip özellikler pipeline'a dahil edilmiştir. Ön işleme adımında ise aykırı değerler (Outliers) baskılanmış ve eksik veriler (NaN) ileriye dönük doldurma yerine silme yöntemiyle temizlenmiştir.

### 6) Final Model vs Baseline Farkı
Hiperparametre optimizasyonu (`RandomizedSearchCV`) ve özellik seçimi sonrası kurulan Final Model, Baseline modele göre RMSE skorunda yaklaşık **%15'lik bir iyileşme** sağlamıştır. Tahminlerin varyansı azalmış ve model ani dalgalanmalara karşı daha dayanıklı hale gelmiştir.

### 7) Business Uyumu
Model çıktısı doğrudan kullanılmamakta, iş gereksinimlerine göre bir **Karar Katmanı (Decision Layer)** içinden geçirilmektedir.
* **Uyum:** Modelin saf tahminine, operasyonel riski sıfıra indirmek için dinamik bir **"Güvenlik Marjı" (Safety Margin)** eklenmektedir. Bu sayede model, sadece matematiksel hatayı değil, finansal riski de minimize etmektedir.

### 8) Canlıya Alma ve İzleme Metrikleri
Proje **Streamlit** ile canlı bir web uygulamasına dönüştürülmüş ve Dockerize edilmiştir.
* **İzleme (Monitoring):** Her tahmin işlemi `monitoring.db` veritabanına loglanmaktadır.
* **Takip Edilmesi Gereken Metrikler:**
    1.  **Data Drift:** Girdi verisinin dağılımının (Örn: `lag_24` ortalaması) eğitim verisinden sapıp sapmadığı.
    2.  **Prediction Drift:** Modelin ürettiği tahminlerin zamanla kayıp kaymadığı.
    3.  **Gerçekleşen Hata:** ATM'den alınan "Gerçekleşen Çekim" verisi geldikçe hesaplanacak günlük RMSE/MAE değeri.

## 🛠️ Kurulum (Local Setup)
Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

**1. Repoyu Klonlayın:**

```
git clone https://github.com/alperaycoker/atm-cash-optimization
cd atm-project
```

**2. Sanal Ortam Oluşturun (Opsiyonel ama önerilir):**

```python -m venv venv```
***Windows için:***
```venv\Scripts\activate```
***Mac/Linux için:***
```source venv/bin/activate```

**3. Gereksinimleri Yükleyin:**
```pip install -r requirements.txt```

**4. Modeli Eğitin (Pipeline):**
***Veriyi işler, modeli eğitir ve models/ klasörüne kaydeder***
```python src/pipeline.py```

**5. Uygulamayı Başlatın:**
```streamlit run app.py```

## 🐳 Docker ile Çalıştırma

Proje Dockerize edilmiştir. Herhangi bir Python kurulumu yapmadan konteyner içinde çalıştırmak için:

**1. İmajı Oluşturun:**

```docker build -t atm-app .```

**2. Konteyneri Başlatın:**

```docker run -p 8501:8501 atm-app```

## 📈 Veri Seti (Data Source)
Projede Kaggle üzerinde yayınlanan ve 359 ATM'nin saatlik işlem verilerini içeren veri seti kullanılmıştır.
* **Link:** [ATM Transactions Dataset](https://www.kaggle.com/datasets/yarenyilmaz/atm-transactions)
* **Boyut:** ~60.000 işlem satırı.

## 👥 İletişim

Geliştirici: Alp Eray

GitHub: [Profilim](https://github.com/alperaycoker)

LinkedIn: [Profilim](https://linkedin.com/in/alperaycoker)
