from typing import List, Optional
from uuid import UUID
from src.domain.entities import Producto, ErrorDeDominio
from src.domain.repositories import RepositorioProducto

class ServicioProducto:
    def __init__(self, repositorio_producto: RepositorioProducto):
        self.repositorio_producto = repositorio_producto

    def crear_producto(self, nombre: str, sku: str, precio: float, stock: int) -> Producto:
        existente = self.repositorio_producto.obtener_por_sku(sku)
        if existente:
            raise ErrorDeDominio(f"Ya existe un producto registrado con el SKU '{sku}'.")
        
        producto = Producto(nombre=nombre, sku=sku, precio=precio, stock=stock)
        return self.repositorio_producto.guardar(producto)

    def obtener_producto(self, producto_id: UUID) -> Optional[Producto]:
        return self.repositorio_producto.obtener_por_id(producto_id)

    def listar_productos(self) -> List[Producto]:
        return self.repositorio_producto.listar_todos()

    def ajustar_stock(self, producto_id: UUID, cantidad: int) -> Producto:
        producto = self.repositorio_producto.obtener_por_id(producto_id)
        if not producto:
            raise ErrorDeDominio("Producto no encontrado.")
        
        producto.actualizar_stock(cantidad)
        return self.repositorio_producto.guardar(producto)

    def eliminar_producto(self, producto_id: UUID) -> bool:
        return self.repositorio_producto.eliminar(producto_id)
