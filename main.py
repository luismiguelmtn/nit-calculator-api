from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

# Montar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class NIT(BaseModel):
    numero: str

def calcular_digito_verificacion(nit: str) -> int:
    # Verificar que el NIT solo contenga números
    if not nit.isdigit():
        raise HTTPException(status_code=400, detail="El NIT debe contener solo números")
    
    # Vector de números para el cálculo (de derecha a izquierda)
    vector = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    
    # Eliminar cualquier cero a la izquierda
    nit = nit.lstrip('0')
    
    # Verificar longitud válida
    if len(nit) > 15:
        raise HTTPException(status_code=400, detail="El NIT es demasiado largo")
    
    # Calcular la suma de productos (de derecha a izquierda)
    suma = 0
    nit_reversed = nit[::-1]  # Invertir el NIT
    for i in range(len(nit)):
        suma += int(nit_reversed[i]) * vector[i]
    
    # Calcular el módulo
    modulo = suma % 11
    
    # Determinar el dígito de verificación
    if modulo == 0 or modulo == 1:
        return modulo
    else:
        return 11 - modulo

@app.post("/calcular-dv")
async def calcular_dv(nit: NIT):
    try:
        dv = calcular_digito_verificacion(nit.numero)
        return {"nit": nit.numero, "digito_verificacion": dv}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})