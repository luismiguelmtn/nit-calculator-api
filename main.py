from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from fastapi.responses import JSONResponse

app = FastAPI()

# Montar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuración de la base de datos
def init_db():
    conn = sqlite3.connect('nit_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nit_searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT NOT NULL,
        digito_verificacion TEXT NOT NULL,
        fecha_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Inicializar la base de datos al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    init_db()

class NITRequest(BaseModel):
    numero: str

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/calcular-dv")
async def calcular_dv(nit_request: NITRequest):
    try:
        nit = nit_request.numero.replace(".", "").replace("-", "").strip()
        
        # Validar que el NIT sea numérico
        if not nit.isdigit():
            raise HTTPException(status_code=400, detail="El NIT debe contener solo números")
        
        # Algoritmo para calcular el dígito de verificación
        # Constantes según la DIAN
        factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
        
        # Asegurar que el NIT tenga la longitud correcta
        if len(nit) > 15:
            raise HTTPException(status_code=400, detail="El NIT no puede tener más de 15 dígitos")
        
        # Calcular la suma ponderada
        suma = 0
        for i in range(len(nit)):
            suma += int(nit[len(nit) - 1 - i]) * factores[i]
        
        # Calcular el módulo 11
        modulo = suma % 11
        
        # Determinar el dígito de verificación
        if modulo == 0:
            dv = 0
        elif modulo == 1:
            dv = 1
        else:
            dv = 11 - modulo
        
        # Guardar en la base de datos
        conn = sqlite3.connect('nit_history.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO nit_searches (nit, digito_verificacion) VALUES (?, ?)",
            (nit, str(dv))
        )
        conn.commit()
        conn.close()
        
        return {"nit": nit, "digito_verificacion": str(dv)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/historial")
async def obtener_historial():
    try:
        conn = sqlite3.connect('nit_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nit, digito_verificacion, fecha_busqueda FROM nit_searches ORDER BY fecha_busqueda DESC LIMIT 10"
        )
        historial = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Formatear la fecha para mostrarla mejor
        for item in historial:
            fecha = datetime.strptime(item['fecha_busqueda'], '%Y-%m-%d %H:%M:%S')
            item['fecha_busqueda'] = fecha.strftime('%d/%m/%Y %H:%M')
        
        return JSONResponse(content={"historial": historial})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))