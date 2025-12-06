import streamlit as st
import pandas as pd
import os
import sqlite3
from datetime import datetime

# --- 1. MODÜL VE AYAR YÜKLEMELERİ ---
try:
    from src.inference import ATMInference
    from src import config # Yapılandırma dosyasını çağırıyoruz
except ImportError as e:
    st.error(f"🚨 HATA: Gerekli modüller bulunamadı: {e}")
    st.info("Lütfen 'src/inference.py' ve 'src/config.py' dosyalarının mevcut olduğundan emin olun.")
    st.stop()

# --- 2. SAYFA AYARLARI ---
st.set_page_config(
    page_title="ATM Nakit Optimizasyonu",
    page_icon="🏧",
    layout="centered"
)

# --- 3. VERİTABANI BAŞLATMA (MONITORING) ---
def init_db():
    # Veritabanı yolunu config dosyasından alıyoruz
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            timestamp TEXT,
            target_date TEXT,
            input_hour INTEGER,
            lag_24 REAL,
            prediction REAL,
            safe_margin REAL,
            business_saving REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 4. YAPAY ZEKA MOTORUNU YÜKLEME ---
@st.cache_resource
def get_inference_engine():
    # Model yolunu config dosyasından alıyoruz
    engine = ATMInference(config.MODEL_PATH)
    return engine

engine = get_inference_engine()

# --- 5. ARAYÜZ BAŞLIĞI ---
st.title("🏧 ATM Nakit Akış Optimizasyonu")
st.markdown("""
Bu sistem, yapay zeka destekli **Nakit Talep Tahmini** yaparak bankaların 
**Atıl Nakit (Idle Cash)** maliyetini ve **Operasyonel Risklerini** minimize eder.
""")

# Model Yükleme Kontrolü
if not getattr(engine, 'model_loaded', False):
    st.error(f"🚨 HATA: Model dosyası bulunamadı!\nAranan Yol: `{config.MODEL_PATH}`")
    st.warning("Çözüm: Terminalde 'python src/pipeline.py' komutunu çalıştırarak modeli eğitin.")
    st.stop()
else:
    st.success(f"✅ Sistem Hazır! AI Motoru Devrede.")

# --- 6. SIDEBAR (KULLANICI GİRİŞLERİ) ---
st.sidebar.header("🗓️ Tahmin Parametreleri")

selected_date = st.sidebar.date_input("Tarih Seçin", datetime.now())
selected_hour = st.sidebar.slider("Saat Seçin", 0, 23, 12)

# Feature Engineering
date_obj = pd.to_datetime(str(selected_date))
day_of_week = date_obj.dayofweek
day_of_month = date_obj.day
is_weekend = 1 if day_of_week >= 5 else 0

st.sidebar.divider()
st.sidebar.subheader("📊 Geçmiş Veri (Simülasyon)")
st.sidebar.info("Gerçek sistemde bu veriler veritabanından otomatik çekilir.")

# Varsayılan değerler
lag_1 = st.sidebar.number_input("1 Saat Önceki Çekim (TL)", value=1500, step=100)
lag_24 = st.sidebar.number_input("Dün Bu Saatteki Çekim (TL)", value=4200, step=100)
rolling_mean_3 = st.sidebar.number_input("Son 3 Saat Ortalaması", value=1800, step=100)
rolling_mean_24 = st.sidebar.number_input("Son 24 Saat Ortalaması", value=3500, step=100)

# --- 7. TAHMİN BUTONU VE ANALİZ ---
if st.button("🚀 Nakit İhtiyacını Analiz Et", use_container_width=True):
    
    # A) DATA DRIFT KONTROLÜ (Config üzerinden)
    drift_detected = False
    if lag_24 > config.MAX_NORMAL_LAG:
        drift_detected = True
        st.warning(f"⚠️ DİKKAT (Data Drift): Girilen '{lag_24} TL' değeri normal sınırların ({config.MAX_NORMAL_LAG} TL) üzerinde.")

    # B) VERİ HAZIRLAMA
    input_data = pd.DataFrame({
        'hour': [selected_hour],
        'day_of_week': [day_of_week],
        'day_of_month': [day_of_month],
        'is_weekend': [is_weekend],
        'lag_1': [lag_1],
        'lag_24': [lag_24],
        'rolling_mean_3': [rolling_mean_3],
        'rolling_mean_24': [rolling_mean_24]
    })
    
    # C) TAHMİN
    prediction = engine.predict(input_data)
    
    # D) SONUÇ GÖSTERİMİ
    st.subheader("🎯 Tahmin Sonuçları")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tahmini İhtiyaç", f"{prediction:,.0f} TL")
    
    with col2:
        # Güvenlik Marjı (Config üzerinden)
        safe_margin = prediction * config.FINANSAL_AYARLAR['GUVENLIK_MARJI_ORANI']
        st.metric("Önerilen Yükleme", f"{safe_margin:,.0f} TL", delta="+%10 Güvenli")
        
    with col3:
        if drift_detected:
            st.metric("Model Güveni", "Düşük ⚠️", delta_color="inverse")
        else:
            st.metric("Model Güveni", "Yüksek ✅")

    # E) FİNANSAL ETKİ ANALİZİ (Config üzerinden)
    st.divider()
    st.subheader("💰 Finansal Etki Analizi")
    
    # Değerleri config'den çekiyoruz
    faiz_orani = config.FINANSAL_AYARLAR['GUNLUK_FAIZ_ORANI']
    op_maliyeti = config.FINANSAL_AYARLAR['OPERASYON_MALIYETI']
    sabit_yukleme = config.FINANSAL_AYARLAR['SABIT_YUKLEME_TUTARI']
    
    cost_ai = safe_margin * faiz_orani
    
    if sabit_yukleme >= prediction:
        cost_trad = sabit_yukleme * faiz_orani
        durum = "Geleneksel yöntem gereksiz fazla nakit tutuyor (Idle Cash)."
    else:
        cost_trad = (sabit_yukleme * faiz_orani) + op_maliyeti
        durum = "Geleneksel yöntemde para yetmedi, operasyon maliyeti oluştu (Stockout)!"

    tasarruf = cost_trad - cost_ai
    
    c1, c2 = st.columns(2)
    c1.error(f"Geleneksel Maliyet: {cost_trad:,.2f} TL")
    c2.success(f"AI Model Maliyeti: {cost_ai:,.2f} TL")
    st.info(f"💡 **Sonuç:** Bu işlemde bankaya **{tasarruf:,.2f} TL** operasyonel tasarruf sağlandı.\n\n*{durum}*")

    # F) LOGGING (VERİTABANINA KAYIT)
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO predictions (timestamp, target_date, input_hour, lag_24, prediction, safe_margin, business_saving)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), str(selected_date), selected_hour, lag_24, prediction, safe_margin, tasarruf))
    conn.commit()
    conn.close()
    st.toast("✅ Tahmin ve sonuçlar veritabanına kaydedildi!")

# --- 8. MODEL AÇIKLANABİLİRLİĞİ (XAI - SHAP) ---
st.divider()
st.subheader("🧠 Modelin Karar Mantığı (XAI)")

# Resim yolu proje yapısında sabittir
shap_image_path = 'notebooks/shap_summary.png'

if os.path.exists(shap_image_path):
    st.image(shap_image_path, caption="SHAP Analizi: Özelliklerin Tahmine Etkisi", use_container_width=True)
    with st.expander("📊 Bu Grafik Nasıl Okunur?"):
        st.markdown("""
        * **En Üstteki Özellik:** Kararı en çok etkileyen faktördür.
        * **Renkler:** Kırmızı = Yüksek Değer, Mavi = Düşük Değer.
        * **Yön:** Sağa yayılım tahmini artırır, sola yayılım azaltır.
        """)
else:
    st.warning("SHAP grafiği bulunamadı. Lütfen 'notebooks/5_evaluation.ipynb' dosyasını çalıştırın.")

# --- 9. MONITORING EKRANI (GEÇMİŞ) ---
st.divider()
st.subheader("📋 Geçmiş Tahmin İzleme (Monitoring)")

if st.checkbox("Log Kayıtlarını Göster"):
    try:
        conn = sqlite3.connect(config.DB_PATH)
        logs = pd.read_sql("SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10", conn)
        conn.close()
        
        if not logs.empty:
            st.dataframe(logs)
            st.caption("Son tahminlerin trendi:")
            st.line_chart(logs['prediction'])
        else:
            st.info("Henüz kayıtlı bir tahmin yok.")
    except Exception as e:
        st.error(f"Veritabanı okuma hatası: {e}")