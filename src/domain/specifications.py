from abc import ABC, abstractmethod

# --- Patrón Base Specification ---
class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool:
        pass

    def __and__(self, other):
        return AndSpecification(self, other)

    def __or__(self, other):
        return OrSpecification(self, other)

    def __invert__(self):
        return NotSpecification(self)

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

class NotSpecification(Specification):
    def __init__(self, spec: Specification):
        self.spec = spec

    def is_satisfied_by(self, candidate) -> bool:
        return not self.spec.is_satisfied_by(candidate)


# --- Especificaciones Concretas para TecnoStock ---

class ActorActivoSpecification(Specification):
    """Verifica si el actor/comprador está activo (activo == 1)."""
    def is_satisfied_by(self, operacion_con_actor) -> bool:
        actor = operacion_con_actor.get("actor")
        return actor is not None and bool(actor.get("activo"))


class OperacionConLineasSpecification(Specification):
    """Verifica que la operación tenga al menos una línea de detalle."""
    def is_satisfied_by(self, operacion_con_detalles) -> bool:
        detalles = operacion_con_detalles.get("detalles", [])
        return len(detalles) > 0


class OperacionAutorizadaSpecification(Specification):
    """Verifica que la operación esté autorizada (autorizado == 1)."""
    def is_satisfied_by(self, operacion) -> bool:
        return bool(operacion.get("autorizado"))


class ActorPreferenteSpecification(Specification):
    """Verifica si el actor es preferente/VIP (es_preferente == 1)."""
    def is_satisfied_by(self, operacion_con_actor) -> bool:
        actor = operacion_con_actor.get("actor")
        return actor is not None and bool(actor.get("es_preferente"))


class TotalMinimoSpecification(Specification):
    """Verifica si el total de la operación es mayor o igual al mínimo requerido (ej. 1500 MXN)."""
    def __init__(self, minimo: float = 1500.0):
        self.minimo = minimo

    def is_satisfied_by(self, datos_operacion) -> bool:
        total = datos_operacion.get("total", 0.0)
        return float(total) >= self.minimo


class PromocionActivaSpecification(Specification):
    """Verifica si la operación tiene promoción activa."""
    def is_satisfied_by(self, operacion) -> bool:
        return bool(operacion.get("promocion_activa"))