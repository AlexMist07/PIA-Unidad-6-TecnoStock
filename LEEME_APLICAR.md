# Cómo aplicar estas correcciones en VS Code — TecnoStock PIA

Fecha: 2026-11-06. Base: commit 11a61df. Entrega PIA: 2026-11-06 23:59. Matrícula: 2134970. Deploy: Render.

## 1. Copiar los archivos
Descomprime `correcciones-tecnostock.zip` y copia cada archivo sobre tu repo,
respetando la ruta. Son archivos COMPLETOS, no parches: reemplaza el archivo
entero en VS Code.

Archivos incluidos (19):
- .github/workflows/ci.yml
- requirements.txt, .env.example, Dockerfile, .dockerignore, docker-compose.yml, demo.py, seed.py
- src/api/main.py, src/api/routers/product_router.py
- src/application/product_service.py
- src/domain/entities.py, src/domain/repositories.py
- src/infrastructure/models.py, src/infrastructure/database.py, src/infrastructure/repositories.py
- tests/test_productos.py, tests/test_reglas_negocio.py, tests/test_state_machine.py
- LEEME_APLICAR.md (este archivo)

## 2. Borrar un archivo viejo
Borra `src/domain/test_state_machine.py` de tu repo. Su contenido ahora vive
en `tests/test_state_machine.py` (ampliado). Si no lo borras, tendrás el test
duplicado y contaminando la cobertura de `src/`.

## 3. Probar en local (antes del push)
```bash
pip install -r requirements.txt
APP_ENV=test python seed.py --reset
pytest --cov=src --cov-fail-under=80 --cov-report=term-missing
```
La cobertura que exige el PIA es >=80%, no 90%.

Para correr la API:
```bash
uvicorn src.api.main:app --reload
```
Swagger: http://localhost:8000/docs
OpenAPI JSON: http://localhost:8000/openapi.json
Health: http://localhost:8000/health  -> {"status": "ok"}

## 4. Push a GitHub
```bash
git add .
git commit -m "fix: correcciones Fase 0 y 1 - Decimal, CI v4/v5, seed con resguardo, tests sin BD viva"
git push origin main
```
Revisa en GitHub Actions que el run quede en verde. El warning de Node 20 debe desaparecer.

## 5. Deploy en Render
- Crea una base de datos Postgres en Render (Free) y un Web Service en Python
  apuntando a este repo, rama main.
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
- Variables: `DATABASE_URL` = la Internal Database URL de tu Postgres en Render,
  `APP_ENV=production`, `PYTHONPATH=.`
- Después del deploy, abre `https://tu-app.onrender.com/docs` para el Swagger
  y `https://tu-app.onrender.com/health` para verificar.
- Importante: en Render NO corras `seed.py` con `--reset` en producción
  (borraría datos). El seed solo con `APP_ENV=test` o `--reset` hace drop_all.

## 6. Qué NO está verificado aquí
Los tests NO se ejecutaron en esta máquina (no tenía FastAPI/SQLAlchemy/Postgres
instalados). La verificación pendiente es correr `pytest` en tu local o en el
CI de GitHub y confirmar que pasan 9 tests de productos + 7 de reglas de
negocio + 7 de máquina de estados, y que la cobertura es >=80%.

## 7. Qué cambió, en una línea por archivo
- ci.yml: checkout v4, setup-python v5, --cov-fail-under=80
- requirements: +requests, alembic, python-dotenv, pytest-cov con pin
- .env.example: limpio, sin pasos de pgAdmin
- Dockerfile: EXPOSE 8000, CMD uvicorn, usuario no-root
- docker-compose: healthcheck de Postgres, sin --reload
- demo.py: sin "11/11 PASSED" inventado, verifica /health y /docs
- entities.py: precio Decimal, precio > 0, SKU strip().upper()
- models.py: Numeric(10,2), checks, version para optimistic locking
- repositories: select() en vez de query(), guardar por id, IntegrityError -> ErrorDeDominio
- product_service: int, no UUID
- main.py: lifespan, /health, handlers 400
- product_router: Decimal, examples=, paginación skip/limit
- seed.py: drop_all solo con APP_ENV=test o --reset, Decimal, rutas Path
- test_productos: assert incondicional, 404, duplicado 400, precio 0
- test_reglas_negocio: sin BD viva, total TEC-O001 = 7748.00 (no 1600.0), spec compuesta afirmada
- test_state_machine: movido a tests/, + CANCELADA como final
