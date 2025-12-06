# 1. Python 3.9'un "slim" (hafifletilmiş) sürümünü baz al
FROM python:3.9-slim

# 2. Konteyner içinde çalışma klasörünü ayarla
WORKDIR /app

# 3. Kütüphane listesini kopyala ve yükle
# --no-cache-dir ile gereksiz önbellek dosyalarını tutma (imaj boyutunu küçültür)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Projedeki diğer tüm dosyaları kopyala
COPY . .

# 5. Streamlit'in varsayılan portunu dışarı aç
EXPOSE 8501

# 6. Konteyner başladığında uygulamayı ayağa kaldır
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]