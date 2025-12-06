# src/inference.py
import pandas as pd
import xgboost as xgb
import os

class ATMInference:
    def __init__(self, model_path):
        self.model = xgb.XGBRegressor()
        if os.path.exists(model_path):
            self.model.load_model(model_path)
            self.model_loaded = True
        else:
            self.model_loaded = False
            print(f"HATA: Model dosyası bulunamadı: {model_path}")

    def predict(self, input_data):
        if not self.model_loaded:
            return 0.0
        
        # DataFrame kontrolü
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
            
        # Tahmin
        pred = self.model.predict(input_data)[0]
        return max(0, float(pred))