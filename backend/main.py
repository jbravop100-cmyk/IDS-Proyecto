from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import os
import sys

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CARGAR MODELOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ajustamos las rutas por si acaso
MODEL_PATH = os.path.join(BASE_DIR, "random_forest_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
PCA_PATH = os.path.join(BASE_DIR, "pca.pkl")
LABEL_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")

print(f"Directorio base: {BASE_DIR}")
model = None

try:
    print("Intentando cargar modelos...")
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    pca = joblib.load(PCA_PATH)
    label_encoder = joblib.load(LABEL_PATH)
    print("✅ ¡Modelos cargados exitosamente!")
except Exception as e:
    print(f"❌ Error cargando modelos: {e}")
    # No detenemos el servidor para poder ver el error en los logs

class TrafficData(BaseModel):
    features: list

@app.get("/")
def home():
    return {"status": "Online", "System": "Sentinel IDS"}

# --- ESTA ES LA RUTA QUE TE FALTA ---
@app.post("/api/predict")
def predict_intrusion(data: TrafficData):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelos de IA no cargados en el servidor.")
    
    try:
        # Pipeline de predicción
        input_data = np.array([data.features])
        scaled_data = scaler.transform(input_data)
        pca_data = pca.transform(scaled_data)
        
        prediction_idx = model.predict(pca_data)[0]
        prediction_label = label_encoder.inverse_transform([prediction_idx])[0]
        
        # Probabilidad
        probs = model.predict_proba(pca_data)
        confianza = np.max(probs) * 100
        
        es_ataque = prediction_label.lower() != "benign"
        
        return {
            "prediction": prediction_label,
            "is_threat": es_ataque,
            "confidence": f"{confianza:.2f}%"
        }
    except Exception as e:
        print(f"Error en predicción: {e}")
        return {"error": str(e)}

@app.post("/api/contact")
def contact(data: dict):
    return {"status": "Recibido"}