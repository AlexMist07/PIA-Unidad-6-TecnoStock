from decimal import Decimal
from typing import List, Optional

from src.domain.entities import ErrorDeDominio, Producto
from src.domain.repositories import RepositorioProducto


class ServicioProducto:
    def __init__(self, repositorio_producto: RepositorioProducto):
        self.repositorio_producto = repositorio_producto

    @staticmethod
    def _normalizar_sku(sku: str) -> str:
        return sku.strip().upper()

    def crear_producto(
        self, nombre: str, sku: str, precio: Decimal, stock: int
    ) -> Producto:
        sku_normalizado = self._normalizar_sku(sku)
        existente = self.repositorio_producto.obtener_por_sku(sku_normalizado)
        if existente:
            raise ErrorDeDominio(
                f"Ya existe un producto registrado con el SKU "
                f"'{sku_normalizado}'."
            )

        producto = Producto(
            nombre=nombre, sku=sku_normalizado, precio=precio, stock=stock
        )
        return self.repositorio_producto.guardar(producto)

    def obtener_producto(self, producto_id: int) -> Optional[Producto]:
        return self.repositorio_producto.obtener_por_id(producto_id)

    def listar_productos(self) -> List[Producto]:
        return self.repositorio_producto.listar_todos()

    def ajustar_stock(self, producto_id: int, cantidad: int) -> Producto:
        """Ajusta el stock con semántica de delta.

        `cantidad` es un delta, no un valor absoluto: un valor positivo
        suma unidades y un valor negativo las resta. Por ejemplo, con
        stock 10, ajustar_stock(id, 5) deja 15 y ajustar_stock(id, -3)
        deja 7. Si el delta dejaría el stock negativo, la entidad
        rechaza la operación con ErrorStockInvalido.
        """
        producto = self.repositorio_producto.obtener_por_id(producto_id)
        if not producto:
            raise ErrorDeDominio("Producto no encontrado.")

        producto.actualizar_stock(cantidad)
        return self.repositorio_producto.guardar(producto)

    def eliminar_producto(self, producto_id: int) -> bool:
        return self.repositorio_producto.eliminar(producto_id)
