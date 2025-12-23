# src/inference.py
import pandas as pd
import xgboost as xgb
import os

class ATMInference:
    def __init__(self, model_path):
        self.model = xgb.Booster()
        if os.path.exists(model_path):
            try:
                self.model.load_model(model_path)
                self.model_loaded = True
            except Exception as e:
                self.model_loaded = False
                print(f"HATA: Model yüklenirken hata oluştu: {e}")
        else:
            self.model_loaded = False
            print(f"HATA: Model dosyası bulunamadı: {model_path}")

    def predict(self, input_data):
        if not self.model_loaded:
            return 0.0
        
        # DataFrame kontrolü
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
            
        # Tahmin (Booster DMatrix bekler)
        dtest = xgb.DMatrix(input_data)
        pred = self.model.predict(dtest)[0]
        return max(0, float(pred))