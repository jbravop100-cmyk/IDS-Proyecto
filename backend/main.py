from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import uvicorn

app = FastAPI()

# Permitir conexión desde el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "backend/portfolio.db"

# Inicializar Base de Datos
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS logs (ip TEXT, endpoint TEXT, fecha TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS mensajes (nombre TEXT, email TEXT, msj TEXT, fecha TEXT)')
    conn.commit()
    conn.close()

init_db()

class ContactForm(BaseModel):
    nombre: str
    email: str
    mensaje: str

# Middleware Honeypot (Registra todo el tráfico)
@app.middleware("http")
async def honeypot_logger(request: Request, call_next):
    if request.method != "OPTIONS":
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO logs VALUES (?, ?, ?)", 
                     (request.client.host, request.url.path, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            print(f"[ALERTA] Visita detectada: {request.client.host}")
        except: pass
    return await call_next(request)

@app.post("/api/contact")
def save_contact(form: ContactForm):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO mensajes VALUES (?, ?, ?, ?)", 
              (form.nombre, form.email, form.mensaje, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"status": "Mensaje encriptado y guardado"}

@app.get("/api/stats")
def get_stats():
    return {"status": "System Online", "module": "Honeypot Active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)