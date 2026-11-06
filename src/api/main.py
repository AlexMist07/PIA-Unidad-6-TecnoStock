from fastapi import FastAPI
from src.infrastructure.database import inicializar_bd
from src.api.routers import product_router

app = FastAPI(title="TecnoStock API", version="1.0.0")

@app.on_event("startup")
def al_iniciar():
    inicializar_bd()

app.include_router(product_router.enrutador)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a TecnoStock API con DDD y FastAPI"}