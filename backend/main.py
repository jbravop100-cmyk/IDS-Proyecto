from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import os
from datetime import datetime

app = FastAPI()

# --- CONFIGURACIÓN CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CARGAR MODELOS DE IA (CEREBRO) ---
# Buscamos los archivos en la misma carpeta donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "random_forest_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
PCA_PATH = os.path.join(BASE_DIR, "pca.pkl")
LABEL_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")

print("--- CARGANDO SISTEMA DE CIBERSEGURIDAD ---")
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    pca = joblib.load(PCA_PATH)
    label_encoder = joblib.load(LABEL_PATH)
    print("✅ Modelos de IA cargados correctamente.")
except Exception as e:
    print(f"❌ ERROR CRÍTICO: No se pudieron cargar los modelos: {e}")
    model = None

# --- ESTRUCTURA DE DATOS ---
class TrafficData(BaseModel):
    features: list

class ContactForm(BaseModel):
    nombre: str
    email: str
    mensaje: str

# --- MIDDLEWARE (HONEYPOT) ---
# Registra cada visita en los logs de Render
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.method != "OPTIONS":
        print(f"[ALERTA HONEYPOT] Tráfico detectado desde IP: {request.client.host} hacia {request.url.path}")
    response = await call_next(request)
    return response

@app.get("/")
def home():
    return {"status": "Online", "System": "Sentinel IDS con Random Forest"}

# --- RUTA DE PREDICCIÓN (LA QUE TE FALTABA) ---
@app.post("/api/predict")
def predict_intrusion(data: TrafficData):
    if model is None:
        raise HTTPException(status_code=500, detail="El sistema de IA no está activo (Modelos no cargados).")
    
    try:
        # 1. Preparar los datos
        input_data = np.array([data.features])
        
        # 2. Escalar y Reducir (Pipeline)
        scaled_data = scaler.transform(input_data)
        pca_data = pca.transform(scaled_data)
        
        # 3. Predecir
        prediction_idx = model.predict(pca_data)[0]
        prediction_label = label_encoder.inverse_transform([prediction_idx])[0]
        
        # 4. Calcular confianza
        probs = model.predict_proba(pca_data)
        confianza = np.max(probs) * 100
        
        # 5. Determinar si es amenaza
        es_ataque = prediction_label.lower() != "benign"
        
        return {
            "prediction": prediction_label,
            "is_threat": es_ataque,
            "confidence": f"{confianza:.2f}%"
        }
    except Exception as e:
        print(f"Error en predicción: {e}")
        return {"error": str(e)}

# --- RUTA DE CONTACTO ---
@app.post("/api/contact")
def save_contact(form: ContactForm):
    # En Render (Gratis) no usamos SQLite persistente, así que solo lo imprimimos en consola segura
    print(f"📩 NUEVO MENSAJE de {form.nombre} ({form.email}): {form.mensaje}")
    return {"status": "Mensaje recibido y registrado en logs seguros."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)