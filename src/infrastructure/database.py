import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/tecnostock_db",
)

# Configurar el motor de SQLAlchemy. pool_pre_ping=True verifica que
# las conexiones del pool sigan vivas antes de usarlas (evita errores
# por conexiones cerradas por Postgres o por el contenedor).
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Fábrica de sesiones para las transacciones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para los modelos
Base = declarative_base()


def inicializar_bd():
    """Crea todas las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)


def obtener_bd():
    """Dependencia de FastAPI para proveer la sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
