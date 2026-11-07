from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.entities import ErrorDeDominio, Producto
from src.domain.repositories import RepositorioProducto
from src.infrastructure.models import ModeloProducto


class RepositorioProductoSqlAlchemy(RepositorioProducto):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _a_dominio(self, modelo: ModeloProducto) -> Producto:
        precio = modelo.precio
        # Numeric(10, 2) ya devuelve Decimal, pero se convierte por
        # seguridad si el driver devolviera float o str.
        if not isinstance(precio, Decimal):
            precio = Decimal(str(precio))
        return Producto(
            id=modelo.id,
            nombre=modelo.nombre,
            sku=modelo.sku,
            precio=precio,
            stock=modelo.stock,
        )

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        modelo = self.sesion.execute(
            select(ModeloProducto).where(ModeloProducto.id == producto_id)
        ).scalar_one_or_none()
        return self._a_dominio(modelo) if modelo else None

    def obtener_por_sku(self, sku: str) -> Optional[Producto]:
        modelo = self.sesion.execute(
            select(ModeloProducto).where(ModeloProducto.sku == sku)
        ).scalar_one_or_none()
        return self._a_dominio(modelo) if modelo else None

    def listar_todos(self) -> List[Producto]:
        modelos = self.sesion.execute(select(ModeloProducto)).scalars().all()
        return [self._a_dominio(m) for m in modelos]

    def guardar(self, producto: Producto) -> Producto:
        # Buscar por id cuando el producto ya existe (actualización);
        # si no tiene id, buscar por SKU, la clave de negocio única.
        modelo = None
        try:
            if producto.id is not None:
                modelo = self.sesion.execute(
                    select(ModeloProducto).where(
                        ModeloProducto.id == producto.id
                    )
                ).scalar_one_or_none()
            if modelo is None and producto.sku:
                modelo = self.sesion.execute(
                    select(ModeloProducto).where(
                        ModeloProducto.sku == producto.sku
                    )
                ).scalar_one_or_none()

            if modelo:
                modelo.sku = producto.sku
                modelo.nombre = producto.nombre
                modelo.precio = producto.precio
                modelo.stock = producto.stock
            else:
                modelo = ModeloProducto(
                    sku=producto.sku,
                    nombre=producto.nombre,
                    precio=producto.precio,
                    stock=producto.stock,
                )
                self.sesion.add(modelo)

            self.sesion.commit()
            self.sesion.refresh(modelo)
        except IntegrityError as exc:
            self.sesion.rollback()
            raise ErrorDeDominio(
                "No se pudo guardar el producto: SKU duplicado o "
                "dato que viola una restricción de la base de datos."
            ) from exc
        return self._a_dominio(modelo)

    def eliminar(self, producto_id: int) -> bool:
        modelo = self.sesion.execute(
            select(ModeloProducto).where(ModeloProducto.id == producto_id)
        ).scalar_one_or_none()
        if not modelo:
            return False
        try:
            self.sesion.delete(modelo)
            self.sesion.commit()
        except IntegrityError as exc:
            self.sesion.rollback()
            raise ErrorDeDominio(
                "No se puede eliminar el producto porque está "
                "referenciado por operaciones existentes."
            ) from exc
        return True
