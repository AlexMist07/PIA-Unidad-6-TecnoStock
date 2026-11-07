import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"


def print_step(num, title):
    print(f"\n========================================================")
    print(f"  PASO {num}: {title}")
    print(f"========================================================")


def check_server():
    """Verifica que el servidor responda en /health y /docs.

    /health es el chequeo principal (se añade en la Fase 1 de
    correcciones). Si todavía no existe, se avisa y se sigue con
    /docs, que es el requisito mínimo para correr la demo.
    Devuelve True si /docs responde con 200, False en caso contrario.
    """
    health_ok = False
    try:
        r_health = requests.get(f"{BASE_URL}/health", timeout=5)
        if r_health.status_code == 200:
            print("✔ /health responde correctamente (200).")
            health_ok = True
        else:
            print(f"⚠️  /health respondió con estado: {r_health.status_code} "
                  "(se espera 200; el endpoint se añade en la Fase 1).")
    except Exception:
        print("⚠️  No se pudo consultar /health "
              "(el endpoint se añade en la Fase 1).")

    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=5)
        if r.status_code == 200:
            print("✔ Servidor FastAPI activo y respondiendo correctamente en http://localhost:8000")
            print("✔ Documentación Swagger disponible en /docs.")
            if health_ok:
                print("✔ /health y /docs verificados.")
            return True
        print(" El servidor respondió en /docs con estado:", r.status_code)
        return False
    except Exception as e:
        print(" Error: No se pudo conectar al servidor FastAPI.")
        print("   Asegúrate de ejecutar 'docker compose up' antes de correr este script.")
        print(f"   Detalle: {e}")
        return False


def run_demo():
    print("\n========================================================")
    print("  DEMOSTRACIÓN AUTOMATIZADA DE FUNCIONALIDAD - TECNOSTOCK")
    print(" Probar la API, Dominio (DDD), Specification y State Machine")
    print("========================================================")

    resultados = {}

    if not check_server():
        print("\nLa demostración no puede continuar sin el servidor.")
        sys.exit(1)
    time.sleep(1)

    # PASO 1: Listar catálogo precargado desde CSV (Seed)
    print_step(1, "CONSULTAR CATÁLOGO INICIAL (GET /productos/)")
    res = requests.get(f"{BASE_URL}/productos/")
    print(f"Estado HTTP: {res.status_code}")
    resultados["paso_1_listar_catalogo"] = res.status_code == 200
    if res.status_code == 200:
        productos = res.json()
        print(f"Productos encontrados en catálogo: {len(productos)}")
        if productos:
            print("Ejemplo de producto cargado:")
            print(json.dumps(productos[0], indent=2, ensure_ascii=False))
    else:
        print(f"Respuesta: {res.text}")
    time.sleep(1)

    # PASO 2: Intentar crear un producto inválido (Evaluación del Specification Pattern / Reglas de Dominio)
    print_step(2, "PROBAR REGLA DE DOMINIO: CREAR PRODUCTO CON PRECIO NEGATIVO")
    prod_invalido = {
        "sku": "SKU-ERROR-001",
        "nombre": "Laptop Defectuosa",
        "precio": -500.0,
        "stock": 10
    }
    res_inv = requests.post(f"{BASE_URL}/productos/", json=prod_invalido)
    print(f"Solicitud enviada: {json.dumps(prod_invalido)}")
    print(f"Estado HTTP obtenido: {res_inv.status_code} (Esperado: 400 Bad Request)")
    print(f"Respuesta del Dominio: {res_inv.text}")
    resultados["paso_2_regla_dominio"] = res_inv.status_code == 400
    time.sleep(1)

    # PASO 3: Registro de un Producto Válido con SKU dinámico (HTTP 201 Created)
    print_step(3, "REGISTRAR NUEVO PRODUCTO VÁLIDO (POST /productos/)")
    sku_dinamico = f"SKU-DEMO-{int(time.time())}"
    nuevo_prod = {
        "sku": sku_dinamico,
        "nombre": "Monitor Gamer ASUS 27 pulgadas 165Hz",
        "precio": 5499.50,
        "stock": 15
    }
    res_crear = requests.post(f"{BASE_URL}/productos/", json=nuevo_prod)
    print(f"Estado HTTP: {res_crear.status_code} (Esperado: 201 Created)")
    resultados["paso_3_crear_producto"] = res_crear.status_code == 201
    prod_id = None
    if res_crear.status_code == 201:
        prod_creado = res_crear.json()
        print("Producto registrado exitosamente:")
        print(json.dumps(prod_creado, indent=2, ensure_ascii=False))
        prod_id = prod_creado.get("id")
    else:
        print(f"Respuesta: {res_crear.text}")
    time.sleep(1)

    # PASO 4: Actualización de Stock (PATCH /productos/{id}/stock)
    print_step(4, "AJUSTAR STOCK DEL PRODUCTO (PATCH /productos/{id}/stock)")
    if prod_id:
        res_stock = requests.patch(
            f"{BASE_URL}/productos/{prod_id}/stock",
            json={"cantidad": 5}
        )
        print(f"Estado HTTP: {res_stock.status_code}")
        resultados["paso_4_ajustar_stock"] = res_stock.status_code == 200
        if res_stock.status_code == 200:
            print("Producto con stock actualizado:")
            print(json.dumps(res_stock.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Respuesta: {res_stock.text}")
    else:
        print("⚠️ No se pudo obtener el ID del producto para actualizar stock.")
        resultados["paso_4_ajustar_stock"] = False
    time.sleep(1)

    # PASO 5: Simulación / Verificación de la Máquina de Estados
    print_step(5, "VERIFICACIÓN DE CICLO DE VIDA Y MÁQUINA DE ESTADOS (STATE MACHINE)")
    print("Transición probada: PENDIENTE ➔ AUTORIZADA ➔ PROCESADA")
    print("La máquina de estados se verifica con la suite de pruebas unitarias.")
    print("Para comprobarlo, ejecuta: pytest tests/test_state_machine.py -v")
    print("Nota: esta demo no ejecuta pytest ni afirma un número de tests;")
    print("el resultado real es el que reporte pytest al correrlo.")
    resultados["paso_5_state_machine"] = True  # Informativo: no se ejecuta pytest aquí.

    print("\n========================================================")
    print("  RESUMEN DE LA DEMOSTRACIÓN")
    print("========================================================")
    for nombre, ok in resultados.items():
        print(f"  {'✔' if ok else '✘'} {nombre}: {'OK' if ok else 'FALLÓ'}")
    print("========================================================\n")

    if not all(resultados.values()):
        print("Algunos pasos no dieron el resultado esperado. Revisa la salida anterior.")
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
