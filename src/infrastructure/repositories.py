from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.entities import Producto
from src.domain.repositories import RepositorioProducto
from src.infrastructure.models import ModeloProducto

class RepositorioProductoSqlAlchemy(RepositorioProducto):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _a_dominio(self, modelo: ModeloProducto) -> Producto:
        return Producto(
            id=modelo.id,
            nombre=modelo.nombre,
            sku=modelo.sku,
            precio=modelo.precio,
            stock=modelo.stock
        )

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        modelo = self.sesion.query(ModeloProducto).filter(ModeloProducto.id == producto_id).first()
        return self._a_dominio(modelo) if modelo else None

    def obtener_por_sku(self, sku: str) -> Optional[Producto]:
        modelo = self.sesion.query(ModeloProducto).filter(ModeloProducto.sku == sku).first()
        return self._a_dominio(modelo) if modelo else None

    def listar_todos(self) -> List[Producto]:
        modelos = self.sesion.query(ModeloProducto).all()
        return [self._a_dominio(m) for m in modelos]

    def guardar(self, producto: Producto) -> Producto:
        # Buscamos por SKU, que es la clave de negocio única en el catálogo de TecnoStock
        modelo = None
        if producto.sku:
            modelo = self.sesion.query(ModeloProducto).filter(ModeloProducto.sku == producto.sku).first()
            
        if modelo:
            modelo.nombre = producto.nombre
            modelo.precio = producto.precio
            modelo.stock = producto.stock
        else:
            modelo = ModeloProducto(
                sku=producto.sku,
                nombre=producto.nombre,
                precio=producto.precio,
                stock=producto.stock
            )
            self.sesion.add(modelo)
            
        self.sesion.commit()
        self.sesion.refresh(modelo)
        return self._a_dominio(modelo)

    def eliminar(self, producto_id: int) -> bool:
        modelo = self.sesion.query(ModeloProducto).filter(ModeloProducto.id == producto_id).first()
        if modelo:
            self.sesion.delete(modelo)
            self.sesion.commit()
            return True
        return False