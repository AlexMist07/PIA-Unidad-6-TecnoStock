import csv
import os
from datetime import datetime
from src.infrastructure.database import SessionLocal, engine
from src.infrastructure.models import Base, ModeloProducto, ModeloActor, ModeloOperacion, ModeloDetalleOperacion

def cargar_todo_el_sistema():
    # 1. Limpiar tablas anteriores y recrearlas limpias con autoincrement
    print("Reiniciando y creando tablas en la base de datos...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    ruta_base = os.path.join("tests", "data")
    db = SessionLocal()

    try:
        print("Iniciando carga masiva de datos oficiales...")

        # 2. Cargar Actores
        ruta_actores = os.path.join(ruta_base, "actores.csv")
        if os.path.exists(ruta_actores):
            with open(ruta_actores, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    actor_id = fila["actor_id"]
                    existente = db.query(ModeloActor).filter(ModeloActor.actor_id == actor_id).first()
                    if not existente:
                        db.add(ModeloActor(
                            actor_id=actor_id,
                            nombre=fila["nombre"],
                            es_preferente=int(fila["es_preferente"]) == 1,
                            activo=int(fila["activo"]) == 1,
                            ciudad=fila["ciudad"]
                        ))
            db.commit()
            print("✔ Actores cargados correctamente.")

        # 3. Cargar Catálogo (Recursos)
        ruta_catalogo = os.path.join(ruta_base, "catalogo.csv")
        if os.path.exists(ruta_catalogo):
            with open(ruta_catalogo, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    sku = fila["recurso_id"]
                    existente = db.query(ModeloProducto).filter(ModeloProducto.sku == sku).first()
                    if not existente:
                        db.add(ModeloProducto(
                            sku=sku,
                            nombre=fila["descripcion"],
                            precio=float(fila["precio_mxn"]),
                            stock=int(fila["capacidad_o_stock"])
                        ))
            db.commit()
            print("✔ Catálogo de productos cargado correctamente.")

        # 4. Cargar Operaciones
        ruta_operaciones = os.path.join(ruta_base, "operaciones.csv")
        if os.path.exists(ruta_operaciones):
            with open(ruta_operaciones, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    op_id = fila["operacion_id"]
                    existente = db.query(ModeloOperacion).filter(ModeloOperacion.operacion_id == op_id).first()
                    if not existente:
                        db.add(ModeloOperacion(
                            operacion_id=op_id,
                            actor_id=fila["actor_id"],
                            estado=fila["estado_inicial"],
                            fecha_solicitud=datetime.strptime(fila["fecha_solicitud"], "%Y-%m-%d").date(),
                            promocion_activa=int(fila["promocion_activa"]) == 1,
                            autorizado=int(fila["autorizado"]) == 1,
                            referencia=fila["referencia"]
                        ))
            db.commit()
            print("✔ Operaciones cargadas correctamente.")

        # 5. Cargar Detalle de Operaciones
        ruta_detalle = os.path.join(ruta_base, "detalle_operaciones.csv")
        if os.path.exists(ruta_detalle):
            with open(ruta_detalle, mode="r", encoding="utf-8-sig") as f:
                for fila in csv.DictReader(f):
                    db.add(ModeloDetalleOperacion(
                        operacion_id=fila["operacion_id"],
                        recurso_id=fila["recurso_id"],
                        cantidad=int(fila["cantidad"])
                    ))
            db.commit()
            print("✔ Detalles de operaciones cargados correctamente.")

        print("¡Base de datos poblada exitosamente con todos los CSVs de TecnoStock!")

    except Exception as e:
        db.rollback()
        print(f"Error crítico durante la carga masiva: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cargar_todo_el_sistema()