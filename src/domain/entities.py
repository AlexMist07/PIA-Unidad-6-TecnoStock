from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
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
    precio: Decimal
    stock: int
    id: Optional[int] = None

    def __post_init__(self):
        # Normalizar SKU antes de validar: sin espacios y en mayúsculas.
        if isinstance(self.sku, str):
            self.sku = self.sku.strip().upper()
        # Normalizar precio a Decimal para no arrastrar floats de dinero.
        if not isinstance(self.precio, Decimal):
            try:
                self.precio = Decimal(str(self.precio))
            except (InvalidOperation, ValueError, TypeError) as exc:
                raise ErrorPrecioInvalido(
                    "El precio del producto debe ser mayor a 0."
                ) from exc
        self.validar()

    def validar(self):
        if self.precio <= 0:
            raise ErrorPrecioInvalido(
                "El precio del producto debe ser mayor a 0."
            )
        if self.stock < 0:
            raise ErrorStockInvalido("El stock inicial no puede ser negativo.")
        if not self.sku or not self.sku.strip():
            raise ErrorDeDominio("El SKU del producto no puede estar vacío.")

    def actualizar_stock(self, cantidad: int):
        """Ajusta el stock con semántica de delta.

        `cantidad` es un delta, no un valor absoluto: un valor positivo
        suma unidades (entrada) y un valor negativo las resta (salida).
        Por ejemplo, con stock 10, actualizar_stock(5) deja 15 y
        actualizar_stock(-3) deja 7. Un delta que dejaría el stock
        negativo se rechaza con ErrorStockInvalido.
        """
        nuevo_stock = self.stock + cantidad
        if nuevo_stock < 0:
            raise ErrorStockInvalido("Stock insuficiente para realizar la operación.")
        self.stock = nuevo_stock
