# Especificación OpenAPI / Swagger - TecnoStock API

## Resumen de Endpoints del Catálogo de Productos

| Método | Endpoint | Descripción | Códigos HTTP |
| :---: | :--- | :--- | :---: |
| `GET` | `/productos/` | Listar catálogo completo precargado. | `200 OK` |
| `POST` | `/productos/` | Registrar un nuevo producto con validación de dominio. | `201 Created`<br>`400 Bad Request` |
| `GET` | `/productos/{id}` | Obtener detalle de un producto por su ID. | `200 OK`<br>`404 Not Found` |
| `PATCH` | `/productos/{id}/stock` | Ajustar o actualizar existencias de inventario. | `200 OK`<br>`400 Bad Request` |
| `DELETE` | `/productos/{id}` | Eliminar producto del catálogo. | `204 No Content`<br>`404 Not Found` |