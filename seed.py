"""Carga masiva de datos oficiales de TecnoStock desde tests/data/*.csv.

Fase 1 (corrección):
- Ya NO se hace ``drop_all()`` incondicional. Borrar todas las tablas
  solo ocurre si ``APP_ENV == "test"`` o si se pasa ``--reset`` como
  argumento (el caso del CI). En cualquier otro caso solo se crean
  las tablas que falten (``create_all``) y la carga es idempotente:
  volver a correr el seed no duplica filas.
- Las rutas se resuelven con ``Path(__file__)`` y ya no dependen del
  directorio de trabajo desde el que se ejecuta el script.
- Los precios se cargan como ``Decimal`` (dinero exacto, no ``float``).
- El detalle de operaciones también verifica duplicados, por
  ``operacion_id`` + ``recurso_id`` (la tabla tiene UNIQUE en ese par).
- Los estados de operación se cargan tal cual vienen en el CSV:
  ``BORRADOR`` está permitido, es el estado inicial del arnés de
  pruebas de operaciones genéricas y ``ModeloOperacion.estado`` es
  String hasta que se conecte la máquina de estados por agregado.
- Nota: la columna ``habilitado`` de ``catalogo.csv`` se ignora porque
  ``ModeloProducto`` no tiene campo ``activo``. Todos los productos
  del catálogo se cargan, incluido TEC-P011 (SSD 11, habilitado = 0).
- Las consultas usan la API ``select()`` de SQLAlchemy 2.0 en vez de
  la API legacy ``session.query()``.
"""

import csv
import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from src.infrastructure.database import SessionLocal, engine
from src.infrastructure.models import (
    Base,
    ModeloActor,
    ModeloDetalleOperacion,
    ModeloOperacion,
    ModeloProducto,
)

RUTA_DATOS = Path(__file__).parent / "tests" / "data"


def _permitir_reset() -> bool:
    """True solo en entorno de pruebas o con el flag explícito --reset.

    En local, correr el seed sin este resguardo borraba toda la base
    de datos en cada ejecución. El CI usa APP_ENV=test (o --reset).
    """
    return os.getenv("APP_ENV") == "test" or "--reset" in sys.argv


def cargar_todo_el_sistema():
    if _permitir_reset():
        print("APP_ENV=test o --reset: reiniciando y creando tablas...")
        Base.metadata.drop_all(bind=engine)
    else:
        print("Creando tablas si no existen (sin borrar datos)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("Iniciando carga masiva de datos oficiales...")

        # 1. Cargar Actores
        ruta_actores = RUTA_DATOS / "actores.csv"
        if ruta_actores.exists():
            with open(ruta_actores, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    actor_id = fila["actor_id"]
                    existente = db.execute(
                        select(ModeloActor).where(
                            ModeloActor.actor_id == actor_id
                        )
                    ).scalar_one_or_none()
                    if not existente:
                        db.add(
                            ModeloActor(
                                actor_id=actor_id,
                                nombre=fila["nombre"],
                                es_preferente=int(fila["es_preferente"]) == 1,
                                activo=int(fila["activo"]) == 1,
                                ciudad=fila["ciudad"],
                            )
                        )
            db.commit()
            print("✔ Actores cargados correctamente.")

        # 2. Cargar Catálogo (Recursos)
        # Nota: la columna "habilitado" del CSV se ignora porque
        # ModeloProducto no tiene campo "activo". Se cargan los 20
        # productos, incluido TEC-P011 (habilitado = 0).
        ruta_catalogo = RUTA_DATOS / "catalogo.csv"
        if ruta_catalogo.exists():
            with open(ruta_catalogo, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    sku = fila["recurso_id"]
                    existente = db.execute(
                        select(ModeloProducto).where(
                            ModeloProducto.sku == sku
                        )
                    ).scalar_one_or_none()
                    if not existente:
                        db.add(
                            ModeloProducto(
                                sku=sku,
                                nombre=fila["descripcion"],
                                precio=Decimal(str(fila["precio_mxn"])),
                                stock=int(fila["capacidad_o_stock"]),
                            )
                        )
            db.commit()
            print("✔ Catálogo de productos cargado correctamente.")

        # 3. Cargar Operaciones
        # El estado se carga tal cual viene en el CSV ("BORRADOR" en las
        # 60 operaciones): es un valor válido hasta que se conecte la
        # máquina de estados por agregado.
        ruta_operaciones = RUTA_DATOS / "operaciones.csv"
        if ruta_operaciones.exists():
            with open(ruta_operaciones, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    op_id = fila["operacion_id"]
                    existente = db.execute(
                        select(ModeloOperacion).where(
                            ModeloOperacion.operacion_id == op_id
                        )
                    ).scalar_one_or_none()
                    if not existente:
                        db.add(
                            ModeloOperacion(
                                operacion_id=op_id,
                                actor_id=fila["actor_id"],
                                estado=fila["estado_inicial"],
                                fecha_solicitud=datetime.strptime(
                                    fila["fecha_solicitud"], "%Y-%m-%d"
                                ).date(),
                                promocion_activa=int(fila["promocion_activa"]) == 1,
                                autorizado=int(fila["autorizado"]) == 1,
                                referencia=fila["referencia"],
                            )
                        )
            db.commit()
            print("✔ Operaciones cargadas correctamente.")

        # 4. Cargar Detalle de Operaciones
        # Se verifica duplicados por (operacion_id, recurso_id), igual
        # que la UNIQUE de la tabla, para que el seed sea idempotente
        # aunque no se haya hecho drop_all().
        ruta_detalle = RUTA_DATOS / "detalle_operaciones.csv"
        if ruta_detalle.exists():
            vistos = set()
            with open(ruta_detalle, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    clave = (fila["operacion_id"], fila["recurso_id"])
                    if clave in vistos:
                        continue
                    vistos.add(clave)
                    existente = db.execute(
                        select(ModeloDetalleOperacion).where(
                            ModeloDetalleOperacion.operacion_id
                            == fila["operacion_id"],
                            ModeloDetalleOperacion.recurso_id
                            == fila["recurso_id"],
                        )
                    ).scalar_one_or_none()
                    if not existente:
                        db.add(
                            ModeloDetalleOperacion(
                                operacion_id=fila["operacion_id"],
                                recurso_id=fila["recurso_id"],
                                cantidad=int(fila["cantidad"]),
                            )
                        )
            db.commit()
            print("✔ Detalles de operaciones cargados correctamente.")

        print("¡Base de datos poblada exitosamente con todos los CSVs de TecnoStock!")

    except Exception as e:
        db.rollback()
        print(f"Error crítico durante la carga masiva: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    cargar_todo_el_sistema()
