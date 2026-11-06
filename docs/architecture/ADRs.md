# Architectural Decision Records (ADRs) - TecnoStock

## Resumen de Decisiones de Arquitectura

| ID | Título | Estado | Patrón / Tecnología | Impacto Principal |
| :---: | :--- | :---: | :--- | :--- |
| **ADR-001** | Adopción de Domain Model + Service Layer | Aceptado | DDD / Layered Architecture | Separación de reglas de negocio frente a infraestructura. |
| **ADR-002** | Agregado `NumeroDeSerie` independiente | Aceptado | Aggregate Root (DDD) | Unicidad global del serial e historial inmutable. |
| **ADR-003** | Reserva de Stock y Concurrencia Optimista | Aceptado | Optimistic Locking | Eliminación total de dobles ventas en apartados. |
| **ADR-004** | Cancelación Batch de Apartados | Aceptado | Batch / Idempotencia | Proceso automático diario para liberar inventario. |
| **ADR-005** | Motor de Devoluciones con Specification | Aceptado | Specification Pattern | Criterios únicos y estandarizados en las 5 sucursales. |
| **ADR-006** | Bitácora de Auditoría por Domain Events | Aceptado | Event-Driven / Append-Only | Trazabilidad inmutable de todas las operaciones. |
| **ADR-007** | Arquitectura en Capas y Adaptadores | Aceptado | Adapter Pattern | Integración limpia con el PdV Windows existente. |

---

## Detalles de Registros

### ADR-001: Selección del Patrón de Lógica de Negocio

| Atributo | Detalle |
| :--- | :--- |
| **Contexto** | Complejidad de 12 reglas implícitas y fallos operativos en el sistema AS-IS. |
| **Decisión** | Implementar **Domain Model** coordinado por una **Service Layer** (FastAPI). |
| **Alternativas Descartadas** | Transaction Script (duplica código), Table Module y Active Record (acoplan a BD). |
| **Consecuencias** | (+) Dominio probado sin base de datos. (-) Mayor curva de aprendizaje inicial. |

---

### ADR-002: Manejo de Números de Serie

| Atributo | Detalle |
| :--- | :--- |
| **Contexto** | Dificultad para rastrear seriales obligatorios en laptops, celulares y tablets. |
| **Decisión** | Modelar `NumeroDeSerie` como Raíz de Agregado con restricción `UNIQUE` en base de datos. |
| **Consecuencias** | (+) Cero seriales duplicados. (+) Historial completo de vida del equipo. |

---

### ADR-003: Control de Concurrencia y Dobles Ventas

| Atributo | Detalle |
| :--- | :--- |
| **Contexto** | Venta por error de artículos apartados con anticipo por otros clientes. |
| **Decisión** | `disponible = total - reservado - dañado`. Concurrencia controlada con versión optimista. |
| **Consecuencias** | (+) Fórmula unificada en el sistema. (+) Garantía de cero dobles ventas. |

---

### ADR-005: Estandarización de Devoluciones

| Atributo | Detalle |
| :--- | :--- |
| **Contexto** | Criterios dispares y subjetivos entre cajeros de las 5 sucursales. |
| **Decisión** | Centralizar reglas (30 días, comprobante, umbral $500) en `PoliticaDevolucionService`. |
| **Consecuencias** | (+) Comportamiento único e imparcial. (+) Aprobación remota de Supervisor. |