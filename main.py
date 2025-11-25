# main.py: Servidor API para el Sistema de Detección de Intrusos (IDS)

from flask import Flask, request, jsonify
from flask_cors import CORS # Importación necesaria para evitar el error 'Failed to fetch'
import joblib
import numpy as np
import os
import sys

# --- 1. Inicialización de Flask y Carga de Modelos ---
app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde cualquier origen
CORS(app) 

# Cargar el modelo y los preprocesadores guardados
try:
    # Obtener el directorio actual para cargar los archivos .pkl
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Se busca el archivo .pkl en la ruta actual
    modelo = joblib.load(os.path.join(current_dir, 'random_forest_model.pkl'))
    scaler = joblib.load(os.path.join(current_dir, 'scaler.pkl'))
    pca = joblib.load(os.path.join(current_dir, 'pca.pkl'))
    le = joblib.load(os.path.join(current_dir, 'label_encoder.pkl'))
    
    print("Modelos y preprocesadores cargados correctamente.")
except FileNotFoundError as e:
    print(f"🚨 ERROR FATAL: No se encontró uno de los archivos .pkl. Asegúrate de que estén en la misma carpeta.")
    sys.exit(1) # Detiene la ejecución si faltan archivos

# --- 2. Endpoint de Prueba (GET) ---
@app.route('/', methods=['GET'])
def home():
    """Un endpoint simple para verificar que el servidor esté activo."""
    return jsonify({
        "status": "online", 
        "message": "API de Detección de Intrusos (IDS) activa. Usa el método POST en /predict."
    })

# --- 3. Definición del Endpoint de Predicción (POST) ---
@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint para recibir una muestra de tráfico de red y retornar la predicción.
    El cuerpo JSON debe contener la clave 'features' con un array de 78 features.
    """
    data = {} # Inicializar data por si la petición falla antes de get_json()
    try:
        data = request.get_json()
        
        # Validar la entrada
        if 'features' not in data:
            raise ValueError('Falta la clave "features" en el cuerpo JSON o está vacía.')

        # Se espera un array de 78 features (debido al entrenamiento de scaler.pkl)
        features = np.array(data['features']).reshape(1, -1)
        
        # Validación de 78 features antes de usar el scaler
        if features.shape[1] != 78:
             raise ValueError(f"Cantidad de features incorrecta. Se esperaban 78 pero se recibieron {features.shape[1]}.")

        # --- APLICAR EL PREPROCESAMIENTO ---
        
        # 1. Normalización (MinMax) - Requiere 78 features
        features_scaled = scaler.transform(features) 
        
        # 2. Reducción de Dimensionalidad (PCA)
        features_pca = pca.transform(features_scaled) 
        
        # 3. Predicción con Random Forest
        prediction_code = modelo.predict(features_pca)[0]
        prediction_proba = modelo.predict_proba(features_pca).max()
        
        # 4. Descodificar la etiqueta
        resultado = le.inverse_transform([prediction_code])[0]
        
        # 5. Retornar el resultado
        return jsonify({
            'prediccion_clase': int(prediction_code),
            'mensaje_alerta': resultado,
            'confianza': float(prediction_proba)
        })

    except Exception as e:
        # Manejo de errores de formato o dimensión
        print(f"\n--- ERROR DE PROCESAMIENTO DETALLADO EN /predict ---")
        print(e)
        print("-----------------------------------------------------")
        
        # Retorna el error al navegador con el código 500
        error_message = f"Error en el procesamiento. Verifique la cantidad (78) y el tipo de datos (números). Detalle: {str(e)}"
        
        return jsonify({
            'error': error_message, 
            'input_received': str(data.get('features')) if data and 'features' in data else 'None'
        }), 500

# --- 4. Ejecución del Servidor Local ---
if __name__ == '__main__':
    print("Iniciando Servidor Flask...")
    # Ejecuta el servidor en el puerto 5000 con modo depuración activado
    app.run(debug=True, port=5000)
    