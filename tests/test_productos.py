"""Tests de la API de productos de TecnoStock.

Fase 1 (corrección):
- ``test_actualizar_stock_producto`` tenía un assert CONDICIONAL
  (``if res_patch.status_code == 200:``): si el PATCH fallaba, el
  test pasaba en vacío (falso positivo). Ahora los asserts son
  incondicionales: el PATCH debe devolver 200 y el stock debe ser 15.
- El PATCH de stock tiene semántica de delta: con stock 10, mandar
  cantidad 5 debe dejar 15.
- Se añaden tests de SKU duplicado (400), obtener por id inexistente
  (404) y precio cero por API (400, porque el dominio exige precio > 0).
- Los precios se mandan como números JSON (Pydantic los convierte a
  Decimal) y se usa un fixture que garantiza que las tablas existan
  aunque el TestClient no dispare el lifespan de la app.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.domain.entities import (
    ErrorPrecioInvalido,
    ErrorStockInvalido,
    Producto,
)
from src.infrastructure.database import inicializar_bd

cliente = TestClient(app)


@pytest.fixture(autouse=True)
def _tablas_existentes():
    """Garantiza que las tablas existan (create_all es idempotente)."""
    inicializar_bd()


def test_leer_raiz():
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Bienvenido a TecnoStock API con DDD y FastAPI"
    }


def test_leer_health():
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_crear_y_listar_producto():
    # Generar un SKU único para evitar conflictos de duplicados en la base de datos
    sku_unico = f"SKU-DELL-{uuid.uuid4().hex[:6].upper()}"

    datos_producto = {
        "nombre": "Laptop Dell Latitude 7490",
        "sku": sku_unico,
        "precio": 8500.0,
        "stock": 10,
    }

    # 1. Crear producto
    respuesta_creacion = cliente.post("/productos/", json=datos_producto)
    assert respuesta_creacion.status_code == 201
    creado = respuesta_creacion.json()
    assert creado["nombre"] == datos_producto["nombre"]
    assert creado["sku"] == sku_unico
    assert float(creado["precio"]) == 8500.0

    # 2. Listar productos y verificar que aparezca
    respuesta_lista = cliente.get("/productos/")
    assert respuesta_lista.status_code == 200
    productos = respuesta_lista.json()
    assert len(productos) > 0
    assert any(p["sku"] == sku_unico for p in productos)


def test_obtener_producto_por_id():
    sku_test = f"SKU-GET-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Mouse Gamer",
        "sku": sku_test,
        "precio": 450.0,
        "stock": 15,
    }
    res_crear = cliente.post("/productos/", json=payload)
    assert res_crear.status_code == 201
    id_producto = res_crear.json()["id"]

    res_obtener = cliente.get(f"/productos/{id_producto}")
    assert res_obtener.status_code == 200
    data = res_obtener.json()
    assert data["sku"] == sku_test


def test_obtener_producto_inexistente_404():
    res_obtener = cliente.get("/productos/999999999")
    assert res_obtener.status_code == 404


def test_actualizar_stock_producto():
    sku_test = f"SKU-STOCK-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Teclado Mecánico",
        "sku": sku_test,
        "precio": 1200.0,
        "stock": 10,
    }
    res_crear = cliente.post("/productos/", json=payload)
    assert res_crear.status_code == 201
    id_producto = res_crear.json()["id"]

    # La cantidad es un DELTA: stock 10 + 5 = 15.
    res_patch = cliente.patch(
        f"/productos/{id_producto}/stock", json={"cantidad": 5}
    )
    # Assert INCONDICIONAL: si el PATCH falla, el test debe fallar.
    assert res_patch.status_code == 200
    assert res_patch.json()["stock"] == 15


def test_actualizar_stock_negativo_no_puede_quedar_negativo():
    sku_test = f"SKU-STOCKNEG-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Teclado Mecánico",
        "sku": sku_test,
        "precio": 1200.0,
        "stock": 2,
    }
    res_crear = cliente.post("/productos/", json=payload)
    assert res_crear.status_code == 201
    id_producto = res_crear.json()["id"]

    # Delta -5 sobre stock 2 dejaría -3: debe rechazarse con 400.
    res_patch = cliente.patch(
        f"/productos/{id_producto}/stock", json={"cantidad": -5}
    )
    assert res_patch.status_code == 400


def test_eliminar_producto():
    sku_test = f"SKU-DEL-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Monitor Genérico",
        "sku": sku_test,
        "precio": 3000.0,
        "stock": 3,
    }
    res_crear = cliente.post("/productos/", json=payload)
    assert res_crear.status_code == 201
    id_producto = res_crear.json()["id"]

    res_delete = cliente.delete(f"/productos/{id_producto}")
    assert res_delete.status_code == 204

    # Después de eliminar, ya no debe existir.
    res_obtener = cliente.get(f"/productos/{id_producto}")
    assert res_obtener.status_code == 404


def test_crear_producto_duplicado_400():
    sku_test = f"SKU-DUP-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Laptop Duplicada",
        "sku": sku_test,
        "precio": 5000.0,
        "stock": 5,
    }
    res_primero = cliente.post("/productos/", json=payload)
    assert res_primero.status_code == 201

    res_segundo = cliente.post("/productos/", json=payload)
    assert res_segundo.status_code == 400


def test_crear_producto_precio_cero_400():
    sku_test = f"SKU-CERO-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Producto Gratis",
        "sku": sku_test,
        "precio": 0,
        "stock": 5,
    }
    res_crear = cliente.post("/productos/", json=payload)
    assert res_crear.status_code == 400


def test_validaciones_dominio_producto():
    with pytest.raises(ErrorPrecioInvalido):
        Producto(nombre="Error Precio", sku="ERR-1", precio=-10.0, stock=5)

    with pytest.raises(ErrorPrecioInvalido):
        Producto(nombre="Error Precio Cero", sku="ERR-0", precio=0, stock=5)

    with pytest.raises(ErrorStockInvalido):
        Producto(nombre="Error Stock", sku="ERR-2", precio=100.0, stock=-5)
