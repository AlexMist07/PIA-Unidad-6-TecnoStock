# TecnoStock API

API REST para la gestión inteligente de inventarios y stock, desarrollada bajo los principios de Domain-Driven Design (DDD) y arquitectura limpia, utilizando FastAPI, PostgreSQL y Docker.

---

## Arquitectura del Proyecto (DDD)

El proyecto está estructurado en capas desacopladas para mantener la lógica de negocio independiente de los detalles de infraestructura:

src/
├── api/              # Controladores, rutas (FastAPI) y esquemas Pydantic
├── application/      # Casos de uso y servicios de aplicación
├── domain/           # Entidades, reglas de negocio, especificaciones y máquina de estados
└── infrastructure/   # Modelos SQLAlchemy, repositorios y conexión a base de datos
tests/                # Pruebas unitarias e integrales con Pytest

---

## Tecnologías y Stack

* Lenguaje: Python 3.10+
* Framework Web: FastAPI
* ORM: SQLAlchemy
* Base de Datos: PostgreSQL
* Contenedorización: Docker y Docker Compose
* Pruebas: Pytest & Pytest-Cov (Cobertura de código > 90%)

---

## Características Principales

1. Gestión de Productos: Creación, listado, consulta por ID, actualización de stock y eliminación mediante identificadores enteros autoincrementables con control estricto de SKU como identificador de negocio.
2. Patrón Specification: Validación de reglas de negocio complejas desacopladas de las entidades.
3. Máquina de Estados (MaquinaEstadosOperacion): Control formal del ciclo de vida de las operaciones (Pendiente, Autorizada, Procesada, Cancelada).
4. Manejo de Excepciones de Dominio: Validación rigurosa de precios y stocks (evitando valores negativos).

---

## Requisitos Previos

Asegúrate de tener instalado en tu equipo:
* Docker
* Docker Compose

---

## Instrucciones de Ejecución

### 1. Clonar el repositorio y configurar variables de entorno
Crea un archivo .env basado en el entorno de Docker (o utiliza los valores por defecto del docker-compose.yml).

### 2. Levantar los servicios con Docker Compose
Ejecuta el siguiente comando en la raíz del proyecto para iniciar la API y la base de datos PostgreSQL:

docker compose up --build -d

### 3. Acceder a la Documentación Interactiva (Swagger UI)
Una vez corriendo los contenedores, abre tu navegador y visita:
http://localhost:8000/docs

---

## Ejecución de Pruebas y Cobertura

Para ejecutar la suite de pruebas unitarias e integrales asegurando el cumplimiento de la cobertura mínima requerida:

docker compose run --rm -e PYTHONPATH=. tests pytest --cov=src --cov-report=term-missing

---

## Autor
Desarrollado como Proyecto Integrador de Aprendizaje (PIA) para la carrera de Ingeniería en Tecnología de Software (ITS) en la Facultad de Ingeniería Mecánica y Eléctrica (FIME) de la Universidad Autónoma de Nuevo León (UANL).
