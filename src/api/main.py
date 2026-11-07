"""Punto de entrada de la API de TecnoStock (FastAPI + DDD).

Fase 1 (corrección):
- Se sustituye el decorador deprecado ``@app.on_event("startup")`` por
  un manejador de ciclo de vida ``lifespan`` (``asynccontextmanager``)
  que crea las tablas al arrancar.
- Se añade el endpoint de salud ``GET /health``.
- Se añaden manejadores globales de errores: las reglas de dominio
  (``ErrorDeDominio``) y las violaciones de integridad de la base de
  datos (``IntegrityError``) devuelven 400 con un detalle claro, en
  lugar de un 500 sin controlar.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.api.routers import product_router
from src.domain.entities import ErrorDeDominio
from src.infrastructure.database import inicializar_bd


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: crea las tablas al arrancar."""
    inicializar_bd()
    yield


app = FastAPI(title="TecnoStock API", version="1.0.0", lifespan=lifespan)


@app.exception_handler(ErrorDeDominio)
async def manejador_error_dominio(request: Request, exc: ErrorDeDominio):
    """Regla de dominio incumplida -> 400 con el mensaje de dominio."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(IntegrityError)
async def manejador_error_integridad(request: Request, exc: IntegrityError):
    """Violación de integridad en base de datos -> 400 con detalle claro."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": (
                "No se pudo completar la operación porque viola una "
                "restricción de integridad de la base de datos "
                "(por ejemplo, un SKU duplicado o un registro "
                "referenciado por otra tabla)."
            )
        },
    )


app.include_router(product_router.enrutador)


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a TecnoStock API con DDD y FastAPI"}


@app.get("/health")
def salud():
    return {"status": "ok"}
