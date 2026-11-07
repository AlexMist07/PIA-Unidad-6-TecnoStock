from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)

from src.infrastructure.database import Base


class ModeloProducto(Base):
    __tablename__ = "productos"

    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_productos_precio_mayor_cero"),
        CheckConstraint("stock >= 0", name="ck_productos_stock_no_negativo"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    # Columna para optimistic locking (ADR-003): se incrementa en cada
    # actualización concurrente. Empieza en 1 para los productos nuevos.
    version = Column(Integer, nullable=False, default=1)


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
    # Estado como String por ahora. Se migrará a Enum cuando se conecte
    # la máquina de estados por agregado (Venta / Apartado / Devolución).
    # El seed carga "BORRADOR" como estado inicial, valor que debe
    # seguir siendo válido hasta esa migración; no romper el seed.
    estado = Column(String, nullable=False)
    fecha_solicitud = Column(Date, nullable=False)
    promocion_activa = Column(Boolean, nullable=False)
    autorizado = Column(Boolean, nullable=False)
    referencia = Column(String, nullable=False)


class ModeloDetalleOperacion(Base):
    __tablename__ = "detalle_operaciones"

    __table_args__ = (
        UniqueConstraint(
            "operacion_id", "recurso_id", name="uq_detalle_operacion_recurso"
        ),
        CheckConstraint("cantidad >= 0", name="ck_detalle_cantidad_no_negativa"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    operacion_id = Column(
        String, ForeignKey("operaciones.operacion_id"), nullable=False
    )
    # FK a productos.sku sin ON DELETE por ahora: el borrado de un
    # producto referenciado se rechaza y lo cubre el handler global
    # de errores en main.py (devuelve 400/409, no 500).
    recurso_id = Column(String, ForeignKey("productos.sku"), nullable=False)
    cantidad = Column(Integer, nullable=False)
