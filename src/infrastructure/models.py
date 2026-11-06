from sqlalchemy import Column, String, Float, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.infrastructure.database import Base

class ModeloProducto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)


class ModeloActor(Base):
    __tablename__ = "actores"

    actor_id = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    es_preferente = Column(Boolean, nullable=False)
    activo = Column(Boolean, nullable=False)
    ciudad = Column(String, nullable=False)


class ModeloOperacion(Base):
    __tablename__ = "operaciones"

    operacion_id = Column(String, primary_key=True, index=True)
    actor_id = Column(String, ForeignKey("actores.actor_id"), nullable=False)
    estado = Column(String, nullable=False)
    fecha_solicitud = Column(Date, nullable=False)
    promocion_activa = Column(Boolean, nullable=False)
    autorizado = Column(Boolean, nullable=False)
    referencia = Column(String, nullable=False)


class ModeloDetalleOperacion(Base):
    __tablename__ = "detalle_operaciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    operacion_id = Column(String, ForeignKey("operaciones.operacion_id"), nullable=False)
    recurso_id = Column(String, ForeignKey("productos.sku"), nullable=False)
    cantidad = Column(Integer, nullable=False)