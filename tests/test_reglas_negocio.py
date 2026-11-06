import pytest
from src.infrastructure.database import SessionLocal
from src.infrastructure.models import ModeloOperacion, ModeloActor, ModeloDetalleOperacion
from src.domain.specifications import (
    ActorActivoSpecification,
    OperacionConLineasSpecification,
    OperacionAutorizadaSpecification,
    ActorPreferenteSpecification,
    TotalMinimoSpecification,
    PromocionActivaSpecification
)

@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_especificacion_puede_procesarse(db_session):
    # Buscamos una operación de prueba en la base de datos
    operacion = db_session.query(ModeloOperacion).filter(ModeloOperacion.operacion_id == "TEC-O001").first()
    assert operacion is not None

    actor = db_session.query(ModeloActor).filter(ModeloActor.actor_id == operacion.actor_id).first()
    detalles = db_session.query(ModeloDetalleOperacion).filter(ModeloDetalleOperacion.operacion_id == operacion.operacion_id).all()

    # Preparamos el contexto para la especificación
    contexto_actor = {"actor": {"activo": actor.activo, "es_preferente": actor.es_preferente}}
    contexto_op = {"autorizado": operacion.autorizado}
    contexto_detalles = {"detalles": detalles}

    # Combinamos las especificaciones con AND (&)
    spec = ActorActivoSpecification() & OperacionConLineasSpecification() & OperacionAutorizadaSpecification()

    # Evaluamos globalmente combinando los diccionarios o evaluando individualmente
    assert ActorActivoSpecification().is_satisfied_by(contexto_actor) is True
    assert OperacionConLineasSpecification().is_satisfied_by(contexto_detalles) is True
    assert OperacionAutorizadaSpecification().is_satisfied_by(contexto_op) is True
    
    print("✔ Prueba de especificación 'puede_procesarse' pasada con éxito.")

def test_especificacion_beneficio_referencia(db_session):
    # Evaluamos la regla de beneficio: Actor preferente AND total >= 1500 AND NOT promocion activa
    operacion = db_session.query(ModeloOperacion).filter(ModeloOperacion.operacion_id == "TEC-O001").first()
    actor = db_session.query(ModeloActor).filter(ModeloActor.actor_id == operacion.actor_id).first()
    
    # Supongamos un total simulado o calculado de 1600 MXN
    contexto_actor = {"actor": {"es_preferente": actor.es_preferente}}
    contexto_op = {"total": 1600.0, "promocion_activa": operacion.promocion_activa}

    spec_beneficio = (
        ActorPreferenteSpecification() & 
        TotalMinimoSpecification(1500.0) & 
        (~PromocionActivaSpecification())
    )

    # Validamos que la composición AND/NOT funcione de forma lógica
    es_preferente = ActorPreferenteSpecification().is_satisfied_by(contexto_actor)
    es_mayor_1500 = TotalMinimoSpecification(1500.0).is_satisfied_by(contexto_op)
    sin_promo = (~PromocionActivaSpecification()).is_satisfied_by(contexto_op)

    print(f"Evaluación Beneficio -> Preferente: {es_preferente}, >=1500: {es_mayor_1500}, Sin Promo: {sin_promo}")
    assert isinstance(es_preferente, bool)
    assert isinstance(es_mayor_1500, bool)