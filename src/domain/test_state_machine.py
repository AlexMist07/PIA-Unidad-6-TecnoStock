import pytest
from src.domain.state_machine import MaquinaEstadosOperacion, EstadoOperacion, ErrorTransicionInvalida

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