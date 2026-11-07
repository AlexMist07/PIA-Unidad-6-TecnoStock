"""Tests de las reglas de negocio (Specifications) de TecnoStock.

Fase 1 (corrección):
- Ya NO se depende de una base de datos viva ni de la operación
  sembrada TEC-O001. Todos los datos son fixtures en memoria,
  tomados de los CSV oficiales del ingeniero (tests/data/).
- El total de la operación se CALCULA desde los precios del catálogo
  en memoria, no se hardcodea. Para TEC-O001 el total real es
  7748.00 MXN (3 x TEC-P009 a 904.00 + 4 x TEC-P014 a 1259.00),
  no 1600.0 como decía el test anterior.
- Se AFIRMA el resultado de la spec compuesta
  (``spec.is_satisfied_by(contexto)``), no solo ``isinstance(bool)``
  de sus componentes.
- Se incluye un caso donde la spec compuesta es False (actor inactivo).

Datos de referencia (tests/data/*.csv):
- TEC-O001: actor TEC-C013 (Comprador 13, es_preferente=0, activo=1),
  autorizado=1, promocion_activa=0, estado BORRADOR.
- Detalle TEC-O001: 3 x TEC-P009 (Laptop 09, 904.00) y
  4 x TEC-P014 (Monitor 14, 1259.00).
"""

from decimal import Decimal

from src.domain.specifications import (
    ActorActivoSpecification,
    ActorPreferenteSpecification,
    OperacionAutorizadaSpecification,
    OperacionConLineasSpecification,
    PromocionActivaSpecification,
    TotalMinimoSpecification,
)

# Precios del catálogo oficial (tests/data/catalogo.csv), en Decimal.
CATALOGO_PRECIOS = {
    "TEC-P009": Decimal("904.00"),
    "TEC-P014": Decimal("1259.00"),
}

# Detalle de la operación TEC-O001 (tests/data/detalle_operaciones.csv).
DETALLES_TEC_O001 = [
    {"recurso_id": "TEC-P009", "cantidad": 3},
    {"recurso_id": "TEC-P014", "cantidad": 4},
]

# Actor de TEC-O001 (tests/data/actores.csv): TEC-C013, no preferente,
# activo, de Monterrey.
ACTOR_TEC_C013 = {
    "actor_id": "TEC-C013",
    "nombre": "Comprador 13",
    "es_preferente": False,
    "activo": True,
    "ciudad": "Monterrey",
}


def calcular_total(detalles):
    """Suma cantidad * precio de catálogo para cada línea de detalle."""
    total = Decimal("0")
    for linea in detalles:
        precio = CATALOGO_PRECIOS[linea["recurso_id"]]
        total += precio * linea["cantidad"]
    return total


def contexto_tec_o001(actor=None):
    """Contexto único (dict) de la operación TEC-O001 para las specs."""
    return {
        "actor": dict(actor if actor is not None else ACTOR_TEC_C013),
        "autorizado": True,
        "promocion_activa": False,
        "detalles": [dict(d) for d in DETALLES_TEC_O001],
        "total": calcular_total(DETALLES_TEC_O001),
    }


def test_calcular_total_tec_o001():
    # 3 x 904.00 = 2712.00 ; 4 x 1259.00 = 5036.00 ; total = 7748.00.
    total = calcular_total(DETALLES_TEC_O001)
    assert total == Decimal("7748.00")


def test_especificacion_puede_procesarse():
    # Regla: actor activo AND operación con líneas AND autorizada.
    contexto = contexto_tec_o001()

    spec = (
        ActorActivoSpecification()
        & OperacionConLineasSpecification()
        & OperacionAutorizadaSpecification()
    )

    # Se afirma el resultado de la spec COMPUESTA, no solo sus partes.
    assert spec.is_satisfied_by(contexto) is True
    assert ActorActivoSpecification().is_satisfied_by(contexto) is True
    assert OperacionConLineasSpecification().is_satisfied_by(contexto) is True
    assert OperacionAutorizadaSpecification().is_satisfied_by(contexto) is True


def test_especificacion_puede_procesarse_actor_inactivo_falsa():
    # Misma operación, pero con el actor inactivo: la regla es False.
    actor_inactivo = dict(ACTOR_TEC_C013, activo=False)
    contexto = contexto_tec_o001(actor=actor_inactivo)

    spec = (
        ActorActivoSpecification()
        & OperacionConLineasSpecification()
        & OperacionAutorizadaSpecification()
    )

    assert ActorActivoSpecification().is_satisfied_by(contexto) is False
    assert spec.is_satisfied_by(contexto) is False


def test_especificacion_beneficio_referencia():
    # Regla de beneficio: actor preferente AND total >= 1500
    # AND NOT promoción activa.
    # TEC-O001: total real 7748.00 (>= 1500) y sin promoción, pero el
    # actor TEC-C013 NO es preferente, así que el beneficio es False.
    contexto = contexto_tec_o001()
    assert contexto["total"] == Decimal("7748.00")

    spec_beneficio = (
        ActorPreferenteSpecification()
        & TotalMinimoSpecification(1500.0)
        & (~PromocionActivaSpecification())
    )

    # Componentes por separado (para diagnosticar si falla la compuesta).
    assert ActorPreferenteSpecification().is_satisfied_by(contexto) is False
    assert TotalMinimoSpecification(1500.0).is_satisfied_by(contexto) is True
    assert (~PromocionActivaSpecification()).is_satisfied_by(contexto) is True

    # Y el resultado de la spec COMPUESTA.
    assert spec_beneficio.is_satisfied_by(contexto) is False


def test_especificacion_beneficio_con_actor_preferente():
    # Misma operación y mismo total, pero con un actor preferente:
    # el beneficio sí aplica.
    actor_preferente = dict(ACTOR_TEC_C013, es_preferente=True)
    contexto = contexto_tec_o001(actor=actor_preferente)
    assert contexto["total"] == Decimal("7748.00")

    spec_beneficio = (
        ActorPreferenteSpecification()
        & TotalMinimoSpecification(1500.0)
        & (~PromocionActivaSpecification())
    )

    assert spec_beneficio.is_satisfied_by(contexto) is True


def test_especificacion_beneficio_con_promocion_activa_falsa():
    # Actor preferente y total suficiente, pero con promoción activa:
    # el beneficio no aplica.
    actor_preferente = dict(ACTOR_TEC_C013, es_preferente=True)
    contexto = contexto_tec_o001(actor=actor_preferente)
    contexto["promocion_activa"] = True

    spec_beneficio = (
        ActorPreferenteSpecification()
        & TotalMinimoSpecification(1500.0)
        & (~PromocionActivaSpecification())
    )

    assert spec_beneficio.is_satisfied_by(contexto) is False


def test_total_minimo_limite():
    # Total exactamente 1500.00: cumple (>= 1500).
    contexto = contexto_tec_o001()
    contexto["total"] = Decimal("1500.00")
    assert TotalMinimoSpecification(1500.0).is_satisfied_by(contexto) is True

    # Total 1499.99: no cumple.
    contexto["total"] = Decimal("1499.99")
    assert TotalMinimoSpecification(1500.0).is_satisfied_by(contexto) is False
