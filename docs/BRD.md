# Business Requirements Document (BRD) - TecnoStock

## 1. Resumen Ejecutivo
TecnoStock es una cadena de 5 sucursales dedicada a la comercialización de electrónica y componentes tecnológicos. Este documento establece los requerimientos de negocio, reglas del dominio y las 17 Historias de Usuario para el sistema de control de inventario, ventas y apartados.

---

## 2. Glosario de Dominio (Lenguaje Ubicuo)

| Término | Nombre en Modelo | Tipo DDD | Descripción |
| :--- | :--- | :--- | :--- |
| **Venta** | `Venta` | Aggregate Root | Transacción comercial donde el cliente paga y recibe su comprobante. |
| **Comprobante** | `Comprobante` | Aggregate Root | Documento que acredita la transacción con folio único secuencial. |
| **Apartado** | `Apartado` | Aggregate Root | Reserva de producto con un anticipo mínimo del 25% y vencimiento a 14 días. |
| **Anticipo** | `Anticipo` | Value Object | Monto inicial pagado para apartar (mínimo 25%, no configurable). |
| **Devolución** | `Devolucion` | Aggregate Root | Proceso de retorno de producto (plazo de 30 días, requiere comprobante o supervisor). |
| **Inventario** | `StockSucursal` | Aggregate Root | Existencias por sucursal. Disponible = Total - Reservado - Dañado - En tránsito. |
| **Número de Serie** | `NumeroDeSerie` | Aggregate Root | Identificador único global obligatorio para computadoras, celulares y tablets. |
| **Producto** | `Producto` | Aggregate Root | Artículo del catálogo identificado por SKU, nombre, precio y política. |
| **Cliente** | `Cliente` | Aggregate Root | Persona que realiza compras, apartados o devoluciones. |
| **Empleado** | `Empleado` | Aggregate Root / VO | Personal de la tienda con rol especificado (Vendedor, Cajero, Supervisor, Almacén). |
| **Sucursal** | `Sucursal` | Aggregate Root | Una de las 5 ubicaciones físicas de venta e inventario. |
| **Método de Pago** | `Pago` / `MetodoPago` | Value Object | Forma de pago (Efectivo, Tarjeta, Transferencia). |
| **Auditoría** | `RegistroAuditoria` | Aggregate (Append-only) | Bitácora inmutable de eventos con timestamp, actor y justificación. |

---

## 3. Matriz de Reglas de Negocio Implícitas

| ID | Regla de Negocio | Tipo de Validación | Impacto en Arquitectura |
| :---: | :--- | :--- | :--- |
| **RN-01** | `Disponible = Total - Reservado` | Cálculo automático | Método `disponible()` en `StockSucursal`. |
| **RN-02** | Serial único global | Restricción inmutable | Restricción `UNIQUE` en BD y Agregado `NumeroDeSerie`. |
| **RN-03** | Vencimiento apartado = 14 días | Fijo / No configurable | Propiedad calculada en entidad `Apartado`. |
| **RN-04** | Bloqueo de producto RESERVADO | Validación de dominio | El Agregado `StockSucursal` rechaza la venta. |
| **RN-05** | Devolución: Comprobante O Supervisor | Validación dinámica | `PoliticaDevolucionService` (Specification). |
| **RN-06** | Plazo límite de devolución = 30 días | Validación temporal | Evaluado en `DevolucionAppService`. |
| **RN-07** | Reembolso por método original | Regla financiera | Mismo `MetodoPago` capturado en la venta. |
| **RN-08** | Supervisor aprueba excepciones | Control de roles | Requerido en montos > $500 o sin comprobante. |
| **RN-09** | Trazabilidad total de auditoría | Bitácora inmutable | Capturado vía Domain Events (`AuditoriaEventHandler`). |
| **RN-10** | Anticipo mínimo del 25% | Validación de entrada | Lanzado en `CalculadoraAnticipo`. |
| **RN-11** | Faltantes > $1000 requieren aprobación | Control de inventario | `ConciliadorInventario` genera reporte. |
| **RN-12** | Cancelación automática de apartados | Proceso Batch | Ejecutado en el cierre de fin de día. |

---

## 4. Historias de Usuario (17 US con Criterios Gherkin)

| ID | Rol | Historia de Usuario | Escenario Gherkin (Criterio de Aceptación) |
| :---: | :--- | :--- | :--- |
| **US01** | Vendedor | Consultar disponibilidad por sucursal | **Dado** que estoy en la terminal<br>**Cuando** busco por código o SKU<br>**Entonces** se muestra disponible y apartado por sucursal. |
| **US02** | Cajero | Procesar pago y generar comprobante | **Dado** que el carrito está listo<br>**Cuando** se confirma el pago<br>**Entonces** descuenta stock y genera folio único. |
| **US03** | Vendedor | Asociar número de serie a la venta | **Dado** que el producto requiere serial<br>**Cuando** se escanea el número de serie<br>**Entonces** valida unicidad y lo asocia a la venta. |
| **US04** | Cliente | Crear apartado con 25% de anticipo | **Dado** un producto disponible<br>**Cuando** el cliente paga el 25% de anticipo<br>**Entonces** cambia a RESERVADO con 14 días de vigencia. |
| **US05** | Sistema | Bloquear venta de producto RESERVADO | **Dado** un producto en estado APARTADO<br>**Cuando** un vendedor intenta venderlo<br>**Entonces** el sistema rechaza la venta. |
| **US06** | Cliente | Liquidar saldo y completar apartado | **Dado** un apartado activo<br>**Cuando** se liquida el saldo pendiente<br>**Entonces** convierte a venta formal y libera el reservado. |
| **US07** | Sistema | Cancelación automática por vencimiento | **Dado** un apartado con 14 días cumplidos<br>**Cuando** se ejecuta el batch de fin de día<br>**Entonces** se marca CANCELADO y libera stock. |
| **US08** | Cliente | Solicitar devolución dentro de 30 días | **Dado** un comprobante < 30 días<br>**Cuando** el producto no tiene daño<br>**Entonces** se procesa cambio o reembolso. |
| **US09** | Supervisor | Autorizar o rechazar devolución | **Dado** una solicitud de devolución<br>**Cuando** no cumple política o supera $500<br>**Entonces** el Supervisor autoriza o rechaza. |
| **US10** | Almacén | Reportar diferencias de inventario | **Dado** un conteo físico<br>**Cuando** la cantidad difiere del sistema<br>**Entonces** crea un reporte de faltante. |
| **US11** | Almacén | Consultar historial de número de serie | **Dado** un número de serie<br>**Cuando** se consulta su historial<br>**Entonces** despliega su trazabilidad completa. |
| **US12** | Cajero | Imprimir comprobante en PdV | **Dado** una venta finalizada<br>**Cuando** se presiona imprimir<br>**Entonces** emite comprobante con formato fiscal. |
| **US13** | Cajero | Cobro en efectivo y cálculo de cambio | **Dado** un pago en efectivo<br>**Cuando** se ingresa el monto recibido<br>**Entonces** calcula el cambio exacto. |
| **US14** | Cajero | Registro de tarjeta o transferencia | **Dado** un pago electrónico<br>**Cuando** se procesa la transacción<br>**Entonces** guarda los últimos 4 dígitos y referencia. |
| **US15** | Vendedor | Consultar apartados del cliente | **Dado** el documento del cliente<br>**Cuando** se consultan sus apartados<br>**Entonces** lista sus reservas activas y vencimientos. |
| **US16** | Supervisor | Transferencia de stock entre sucursales | **Dado** mercancía en Sucursal A<br>**When** se transfiere a Sucursal B<br>**Entonces** bloquea la cantidad como "En Tránsito". |
| **US17** | Supervisor | Reporte consolidado por sucursal | **Dado** la vista de supervisión<br>**Cuando** se consulta el inventario<br>**Entonces** desglose por sucursal (Disponible vs Apartado). |