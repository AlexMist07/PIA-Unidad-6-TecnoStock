from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.entities import Producto

class RepositorioProducto(ABC):
    @abstractmethod
    def obtener_por_id(self, producto_id: UUID) -> Optional[Producto]:
        pass

    @abstractmethod
    def obtener_por_sku(self, sku: str) -> Optional[Producto]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Producto]:
        pass

    @abstractmethod
    def guardar(self, producto: Producto) -> Producto:
        pass

    @abstractmethod
    def eliminar(self, producto_id: UUID) -> bool:
        pass
