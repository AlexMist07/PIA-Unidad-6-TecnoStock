from enum import Enum

class EstadoOperacion(str, Enum):
    PENDIENTE = "PENDIENTE"
    AUTORIZADA = "AUTORIZADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"

class ErrorTransicionInvalida(Exception):
    """Excepción de dominio lanzada cuando se intenta un cambio de estado no permitido."""
    pass

class MaquinaEstadosOperacion:
    """Implementación de la máquina de estados para el ciclo de vida de las operaciones."""
    
    # Matriz de transiciones permitidas
    TRANSICIONES_VALIDAS = {
        EstadoOperacion.PENDIENTE: [EstadoOperacion.AUTORIZADA, EstadoOperacion.CANCELADA],
        EstadoOperacion.AUTORIZADA: [EstadoOperacion.PROCESADA, EstadoOperacion.CANCELADA],
        EstadoOperacion.PROCESADA: [],  # Estado final
        EstadoOperacion.CANCELADA: []   # Estado final
    }

    def __init__(self, estado_actual: EstadoOperacion = EstadoOperacion.PENDIENTE):
        self.estado_actual = estado_actual

    def cambiar_estado(self, nuevo_estado: EstadoOperacion):
        if nuevo_estado not in self.TRANSICIONES_VALIDAS.get(self.estado_actual, []):
            raise ErrorTransicionInvalida(
                f"Transición no permitida: No se puede cambiar de '{self.estado_actual}' a '{nuevo_estado}'."
            )
        self.estado_actual = nuevo_estado