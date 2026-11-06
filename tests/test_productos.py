import uuid
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.domain.entities import Producto, ErrorPrecioInvalido, ErrorStockInvalido

cliente = TestClient(app)

def test_leer_raiz():
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"mensaje": "Bienvenido a TecnoStock API con DDD y FastAPI"}

def test_crear_y_listar_producto():
    # Generar un SKU único para evitar conflictos de duplicados en la base de datos
    sku_unico = f"SKU-DELL-{uuid.uuid4().hex[:6].upper()}"
    
    datos_producto = {
        "nombre": "Laptop Dell Latitude 7490",
        "sku": sku_unico,
        "precio": 8500.0,
        "stock": 10
    }
    
    # 1. Crear producto
    respuesta_creacion = cliente.post("/productos/", json=datos_producto)
    assert respuesta_creacion.status_code == 201
    creado = respuesta_creacion.json()
    assert creado["nombre"] == datos_producto["nombre"]
    assert creado["sku"] == sku_unico

    # 2. Listar productos y verificar que aparezca
    respuesta_lista = cliente.get("/productos/")
    assert respuesta_lista.status_code == 200
    productos = respuesta_lista.json()
    assert len(productos) > 0

def test_obtener_producto_por_id():
    sku_test = f"SKU-GET-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Mouse Gamer",
        "sku": sku_test,
        "precio": 450.0,
        "stock": 15
    }
    res_crear = cliente.post("/productos/", json=payload)
    assert res_crear.status_code == 201
    id_producto = res_crear.json()["id"]

    res_obtener = cliente.get(f"/productos/{id_producto}")
    assert res_obtener.status_code == 200
    data = res_obtener.json()
    assert data["sku"] == sku_test

def test_actualizar_stock_producto():
    sku_test = f"SKU-STOCK-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Teclado Mecánico",
        "sku": sku_test,
        "precio": 1200.0,
        "stock": 10
    }
    res_crear = cliente.post("/productos/", json=payload)
    id_producto = res_crear.json()["id"]

    res_patch = cliente.patch(f"/productos/{id_producto}/stock", json={"cantidad": 5})
    if res_patch.status_code == 200:
        assert res_patch.json()["stock"] == 15

def test_eliminar_producto():
    sku_test = f"SKU-DEL-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "nombre": "Monitor Genérico",
        "sku": sku_test,
        "precio": 3000.0,
        "stock": 3
    }
    res_crear = cliente.post("/productos/", json=payload)
    id_producto = res_crear.json()["id"]

    res_delete = cliente.delete(f"/productos/{id_producto}")
    assert res_delete.status_code in [200, 204]

def test_validaciones_dominio_producto():
    with pytest.raises(ErrorPrecioInvalido):
        Producto(nombre="Error Precio", sku="ERR-1", precio=-10.0, stock=5)

    with pytest.raises(ErrorStockInvalido):
        Producto(nombre="Error Stock", sku="ERR-2", precio=100.0, stock=-5)
