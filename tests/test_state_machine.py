"""Tests de la máquina de estados de operaciones de TecnoStock.

Fase 1 (corrección): este archivo vivía en ``src/domain/`` y
contaminaba el paquete de dominio (y su cobertura). Se mueve a
``tests/`` con el mismo contenido original, ampliado con tests de
CANCELADA como estado final y de las transiciones hacia CANCELADA.

Matriz de transiciones (src/domain/state_machine.py):
- PENDIENTE -> AUTORIZADA, CANCELADA
- AUTORIZADA -> PROCESADA, CANCELADA
- PROCESADA -> (final, sin salidas)
- CANCELADA -> (final, sin salidas)
"""

import pytest

from src.domain.state_machine import (
    ErrorTransicionInvalida,
    EstadoOperacion,
    MaquinaEstadosOperacion,
)


def test_transicion_valida():
    maquina = MaquinaEstadosOperacion(EstadoOperacion.PENDIENTE)

    # Transición de PENDIENTE a AUTORIZADA
    maquina.cambiar_estado(EstadoOperacion.AUTORIZADA)
    assert maquina.estado_actual == EstadoOperacion.AUTORIZADA

    # Transición de AUTORIZADA a PROCESADA
    maquina.cambiar_estado(EstadoOperacion.PROCESADA)
    assert maquina.estado_actual == EstadoOperacion.PROCESADA


def test_transicion_invalida():
    maquina = MaquinaEstadosOperacion(EstadoOperacion.PENDIENTE)

    # Intentar saltar directo de PENDIENTE a PROCESADA (debe fallar)
    with pytest.raises(ErrorTransicionInvalida):
        maquina.cambiar_estado(EstadoOperacion.PROCESADA)


def test_estado_final_sin_salidas():
    maquina = MaquinaEstadosOperacion(EstadoOperacion.PROCESADA)

    # Intentar cambiar de un estado final (PROCESADA) a cualquier otro debe fallar
    with pytest.raises(ErrorTransicionInvalida):
        maquina.cambiar_estado(EstadoOperacion.PENDIENTE)


def test_transicion_a_cancelada_desde_pendiente():
    maquina = MaquinaEstadosOperacion(EstadoOperacion.PENDIENTE)
    maquina.cambiar_estado(EstadoOperacion.CANCELADA)
    assert maquina.estado_actual == EstadoOperacion.CANCELADA


def test_transicion_a_cancelada_desde_autorizada():
    maquina = MaquinaEstadosOperacion(EstadoOperacion.AUTORIZADA)
    maquina.cambiar_estado(EstadoOperacion.CANCELADA)
    assert maquina.estado_actual == EstadoOperacion.CANCELADA


def test_cancelada_es_estado_final_sin_salidas():
    # CANCELADA es un estado final: no puede salir hacia ningún estado,
    # ni siquiera de vuelta a PENDIENTE o a AUTORIZADA.
    maquina = MaquinaEstadosOperacion(EstadoOperacion.CANCELADA)

    with pytest.raises(ErrorTransicionInvalida):
        maquina.cambiar_estado(EstadoOperacion.PENDIENTE)

    with pytest.raises(ErrorTransicionInvalida):
        maquina.cambiar_estado(EstadoOperacion.AUTORIZADA)

    with pytest.raises(ErrorTransicionInvalida):
        maquina.cambiar_estado(EstadoOperacion.PROCESADA)

    # Y tampoco puede "cancelarse" a sí misma.
    with pytest.raises(ErrorTransicionInvalida):
        maquina.cambiar_estado(EstadoOperacion.CANCELADA)


def test_estado_inicial_por_defecto_es_pendiente():
    maquina = MaquinaEstadosOperacion()
    assert maquina.estado_actual == EstadoOperacion.PENDIENTE
