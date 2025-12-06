import os
import pytest
# Basit bir varlık kontrolü testi
def test_data_exists():
    assert os.path.exists('data/atm_data.csv'), "Veri dosyası eksik!"

def test_model_exists():
    # Modeli pipeline çalıştıktan sonra kontrol eder
    assert os.path.exists('models/atm_optimized_model.json'), "Model dosyası oluşturulmamış!"