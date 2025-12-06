# src/config.py
import os

# --- 1. DOSYA YOLLARI (PATHS) ---
# Projenin ana klasörünü otomatik bulur
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, 'data', 'atm_data.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'atm_optimized_model.json')
DB_PATH = os.path.join(BASE_DIR, 'monitoring.db')

# --- 2. İŞ KURALLARI (BUSINESS RULES) ---
# app.py'ın beklediği "FINANSAL_AYARLAR" sözlüğü:
FINANSAL_AYARLAR = {
    "GUNLUK_FAIZ_ORANI": 0.0005,      # %0.05
    "OPERASYON_MALIYETI": 500,        # TL
    "SABIT_YUKLEME_TUTARI": 50000,    # TL (Geleneksel Yöntem)
    "GUVENLIK_MARJI_ORANI": 1.10      # %10 Fazla yükleme (Hata burada çıkıyordu)
}

# --- 3. MODEL AYARLARI ---
# Drift Detection için uyarı eşiği
MAX_NORMAL_LAG = 60000       # TL