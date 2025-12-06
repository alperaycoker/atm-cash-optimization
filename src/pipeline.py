# src/pipeline.py

import pandas as pd
import xgboost as xgb
import os
import sys
import warnings

# Gereksiz uyarıları gizle
warnings.filterwarnings('ignore')

# --- 1. OTOMATİK YOL BULUCU (PATH CONFIG) ---
# Bu scriptin nerede olduğunu bul (src klasörü)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Bir üst klasöre çık (Proje ana dizini)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Yolları buna göre dinamik oluştur
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'atm_data.csv')
MODEL_DIR = os.path.join(PROJECT_ROOT, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'atm_optimized_model.json')

def run_pipeline():
    print("="*50)
    print(f"🚀 ATM NAKİT OPTİMİZASYON PİPELİNE BAŞLATILIYOR")
    print(f"📂 Çalışma Dizini: {PROJECT_ROOT}")
    print("="*50)

    # --- 2. VERİ YÜKLEME ---
    print(f"📊 Veri okunuyor: {DATA_PATH}")
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ HATA: Dosya bulunamadı -> {DATA_PATH}")
        print("ÇÖZÜM: 'data' klasörünün içinde 'atm_data.csv' dosyasının olduğundan emin olun.")
        return

    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✅ Veri yüklendi. Boyut: {df.shape}")
    except Exception as e:
        print(f"❌ Veri okuma hatası: {e}")
        return

    # --- 3. VERİ ÖN İŞLEME VE FEATURE ENGINEERING ---
    print("⚙️  Veri işleniyor ve özellikler türetiliyor...")
    
    # Sütun isim kontrolü (Kaggle verisine göre)
    # Eğer transactionTime yoksa uygun sütunu bulmaya çalışırız
    time_col = 'transactionTime' if 'transactionTime' in df.columns else None
    
    if time_col:
        df[time_col] = pd.to_datetime(df[time_col])
        # Time Series için sıralama şart
        df.sort_values(by=['atmName', time_col], inplace=True)
        
        # Tarihsel Özellikler
        df['hour'] = df[time_col].dt.hour
        df['day_of_week'] = df[time_col].dt.dayofweek
        df['day_of_month'] = df[time_col].dt.day
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    else:
        print("❌ HATA: 'transactionTime' sütunu bulunamadı!")
        return

    # Lag Features (Geçmişe bakış)
    # Her ATM kendi içinde değerlendirilmeli
    df['lag_1'] = df.groupby('atmName')['totalOutcome'].shift(1)
    df['lag_24'] = df.groupby('atmName')['totalOutcome'].shift(24)
    
    # Rolling Features (Hareketli Ortalamalar)
    df['rolling_mean_3'] = df.groupby('atmName')['totalOutcome'].transform(lambda x: x.shift(1).rolling(3).mean())
    df['rolling_mean_24'] = df.groupby('atmName')['totalOutcome'].transform(lambda x: x.shift(1).rolling(24).mean())
    
    # NaN değerleri temizle (Lag işlemleri yüzünden ilk satırlar boşalır)
    initial_len = len(df)
    df.dropna(inplace=True)
    print(f"✅ Ön işleme tamamlandı. {initial_len - len(df)} satır (NaN) temizlendi.")

    # --- 4. MODEL EĞİTİMİ (TRAINING) ---
    print("🧠 Model eğitiliyor (XGBoost)...")
    
    # Modelin kullanacağı özellikler
    features = ['hour', 'day_of_week', 'day_of_month', 'is_weekend', 
                'lag_1', 'lag_24', 'rolling_mean_3', 'rolling_mean_24']
    target = 'totalOutcome'
    
    X = df[features]
    y = df[target]
    
    # Optimizasyon notebook'unda bulduğumuz en iyi parametreleri buraya yazabiliriz
    # Şimdilik genel geçer iyi ayarlar kullanıyoruz
    model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    
    model.fit(X, y)
    print("✅ Model eğitimi tamamlandı.")

    # --- 5. MODELİ KAYDETME ---
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print(f"📂 '{MODEL_DIR}' klasörü oluşturuldu.")
        
    model.save_model(MODEL_PATH)
    print(f"💾 Model başarıyla kaydedildi: {MODEL_PATH}")
    print("="*50)
    print("🎉 PİPELİNE BAŞARIYLA TAMAMLANDI!")
    print("Artık 'streamlit run app.py' komutuyla uygulamayı başlatabilirsiniz.")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()