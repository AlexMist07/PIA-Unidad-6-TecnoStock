from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.orm import Session
from src.infrastructure.database import obtener_bd
from src.infrastructure.repositories import RepositorioProductoSqlAlchemy
from src.application.product_service import ServicioProducto
from src.domain.entities import ErrorDeDominio

enrutador = APIRouter(prefix="/productos", tags=["Gestión de Catálogo - TecnoStock"])

class ProductoCrear(BaseModel):
    nombre: str = Field(..., example="Monitor Gamer ASUS 27 pulgadas 165Hz", description="Nombre descriptivo del producto")
    sku: str = Field(..., example="SKU-DEMO-2026", description="Código SKU único de inventario")
    precio: float = Field(..., example=5499.50, description="Precio unitario en MXN (debe ser mayor a 0)")
    stock: int = Field(..., example=15, description="Cantidad inicial en inventario")

class StockActualizar(BaseModel):
    cantidad: int = Field(..., example=5, description="Cantidad a ajustar en el inventario")

class ProductoRespuesta(BaseModel):
    id: int = Field(..., example=22)
    sku: str = Field(..., example="SKU-DEMO-2026")
    nombre: str = Field(..., example="Monitor Gamer ASUS 27 pulgadas 165Hz")
    precio: float = Field(..., example=5499.50)
    stock: int = Field(..., example=15)

    class Config:
        from_attributes = True

def obtener_servicio_producto(db: Session = Depends(obtener_bd)) -> ServicioProducto:
    repo = RepositorioProductoSqlAlchemy(db)
    return ServicioProducto(repo)

@enrutador.post(
    "/", 
    response_model=ProductoRespuesta, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo producto en el catálogo",
    description="Crea un recurso nuevo validando las reglas de dominio (precios/stocks positivos) y asegurando la unicidad del SKU.",
    responses={
        201: {
            "description": "¡Producto creado con éxito en el sistema!",
        },
        400: {
            "description": "Error por regla de dominio (ej. precio negativo o SKU duplicado)",
            "content": {
                "application/json": {
                    "examples": {
                        "duplicado": {
                            "summary": "SKU ya existente",
                            "value": {"detail": "Ya existe un producto registrado con el SKU 'SKU-DEMO-2026'."}
                        },
                        "precio_invalido": {
                            "summary": "Precio negativo o cero",
                            "value": {"detail": "El precio del producto no puede ser negativo."}
                        }
                    }
                }
            }
        }
    }
)
def crear_producto(carga: ProductoCrear, servicio: ServicioProducto = Depends(obtener_servicio_producto)):
    try:
        producto = servicio.crear_producto(carga.nombre, carga.sku, carga.precio, carga.stock)
        return producto
    except ErrorDeDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@enrutador.get(
    "/", 
    response_model=List[ProductoRespuesta],
    summary="Listar todo el catálogo de productos",
    description="Devuelve la lista completa de todos los productos cargados mediante el seed inicial o registrados en la base de datos."
)
def listar_productos(servicio: ServicioProducto = Depends(obtener_servicio_producto)):
    return servicio.listar_productos()

@enrutador.get(
    "/{producto_id}", 
    response_model=ProductoRespuesta,
    summary="Obtener detalle de un producto por ID",
    description="Busca y retorna la información específica de un producto utilizando su identificador único numérico."
)
def obtener_producto(producto_id: int, servicio: ServicioProducto = Depends(obtener_servicio_producto)):
    producto = servicio.obtener_producto(producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró ningún producto con el ID especificado.")
    return producto

@enrutador.patch(
    "/{producto_id}/stock", 
    response_model=ProductoRespuesta,
    summary="Actualizar o ajustar el inventario de un producto",
    description="Permite modificar la cantidad disponible en stock para un producto existente en el sistema."
)
def ajustar_stock(producto_id: int, carga: StockActualizar, servicio: ServicioProducto = Depends(obtener_servicio_producto)):
    try:
        producto = servicio.ajustar_stock(producto_id, carga.cantidad)
        return producto
    except ErrorDeDominio as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@enrutador.delete(
    "/{producto_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto del catálogo",
    description="Remueve permanentemente un producto de la base de datos utilizando su ID."
)
def eliminar_producto(producto_id: int, servicio: ServicioProducto = Depends(obtener_servicio_producto)):
    exito = servicio.eliminar_producto(producto_id)
    if not exito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró ningún producto con el ID especificado para eliminar.")
    return None