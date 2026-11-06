from dataclasses import dataclass, field
from typing import Optional

class ErrorDeDominio(Exception):
    pass

class ErrorStockInvalido(ErrorDeDominio):
    pass

class ErrorPrecioInvalido(ErrorDeDominio):
    pass

@dataclass
class Producto:
    nombre: str
    sku: str
    precio: float
    stock: int
    id: Optional[int] = None

    def __post_init__(self):
        self.validar()

    def validar(self):
        if self.precio < 0:
            raise ErrorPrecioInvalido("El precio del producto no puede ser negativo.")
        if self.stock < 0:
            raise ErrorStockInvalido("El stock inicial no puede ser negativo.")
        if not self.sku.strip():
            raise ErrorDeDominio("El SKU del producto no puede estar vacío.")

    def actualizar_stock(self, cantidad: int):
        nuevo_stock = self.stock + cantidad
        if nuevo_stock < 0:
            raise ErrorStockInvalido("Stock insuficiente para realizar la operación.")
        self.stock = nuevo_stock
