"""
cliente.py — Guion de demostración end-to-end de la Agencia de Agentes.

Este script ejecuta el circuito completo sin intervención manual:
crea un agente, le asigna una misión, la completa, pide su briefing
y envía un mensaje. También demuestra que sin API key se obtiene 401.

Para correrlo, primero levanta el servidor en otra terminal:
    uvicorn main:app --reload
Y luego ejecuta este archivo:
    python cliente.py
"""

import os
import sys

import requests
from dotenv import load_dotenv

# Cargo el .env para leer la API key sin hardcodearla en el código.
load_dotenv()

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("AGENCIA_API_KEY", "agencia-key-dev")
HEADERS = {"X-API-KEY": API_KEY}


# ── Funciones del guion ───────────────────────────────────────────────────────

def verificar_servidor() -> None:
    """Paso 1: confirma que el servidor responde antes de continuar.
    Si falla acá, el ConnectionError del bloque principal lo captura
    y le da al usuario un mensaje claro de qué hacer.
    """
    resp = requests.get(f"{BASE_URL}/")
    resp.raise_for_status()
    print(f"[1] Servidor activo: {resp.json()}")


def crear_agente(nombre: str, rol: str, energia: int) -> bool:
    """Paso 2: registra un agente nuevo usando la API key en el header.
    Retorna True si el servidor respondió 200 o 201.
    """
    datos = {"nombre": nombre, "rol": rol, "energia": energia}
    resp = requests.post(f"{BASE_URL}/agentes/", json=datos, headers=HEADERS)
    resultado = resp.json()
    print(f"[2] Crear agente '{nombre}': {resultado.get('mensaje', resultado)}")
    return resp.status_code in (200, 201)


def consultar_agente_http(nombre: str) -> dict | None:
    """Paso 3: confirma que el agente quedó guardado consultando su endpoint.
    Retorna el diccionario del agente o None si no se encontró.
    Heredada de S5_cliente.py — misma lógica, mismo propósito.
    """
    resp = requests.get(f"{BASE_URL}/agente/{nombre}")
    if resp.status_code == 200:
        return resp.json()
    if resp.status_code == 404:
        print(f"     [Cliente] Agente '{nombre}' no encontrado (404)")
        return None
    print(f"     [Cliente] Error inesperado: {resp.status_code}")
    return None


def crear_mision(
    titulo: str,
    descripcion: str,
    agente: str,
    energia_requerida: int,
    prioridad: int = 3,
) -> int | None:
    """Paso 4: crea una misión y retorna el id que devuelve el servidor.
    Necesito ese id para el paso siguiente — completar la misión.
    """
    datos = {
        "titulo": titulo,
        "descripcion": descripcion,
        "agente_asignado": agente,
        "estado": "pendiente",
        "energia_requerida": energia_requerida,
        "prioridad": prioridad,
        "recompensa": 10,
    }
    resp = requests.post(f"{BASE_URL}/misiones/", json=datos, headers=HEADERS)
    resultado = resp.json()
    mision_id = resultado.get("id")
    print(f"[4] Misión creada: id={mision_id} | {resultado.get('mensaje', resultado)}")
    return mision_id


def completar_mision(mision_id: int) -> bool:
    """Paso 5: completa la misión. El servidor reconstruye el agente,
    llama a completar_mision() en la clase y descuenta la energía.
    En la respuesta viene cuánta energía le quedó y si era admin.
    """
    resp = requests.post(
        f"{BASE_URL}/misiones/{mision_id}/completar", headers=HEADERS
    )
    resultado = resp.json()
    print(f"[5] Completar misión id={mision_id}: {resultado.get('mensaje', resultado)}")
    if resp.status_code == 200:
        print(
            f"     Agente: {resultado.get('agente')} | "
            f"Energía restante: {resultado.get('energia_restante')} | "
            f"Es admin: {resultado.get('es_admin')}"
        )
    return resp.status_code == 200


def consultar_briefing(nombre: str) -> None:
    """Paso 6: trae el briefing completo del agente — sus datos locales
    más un consejo de la API externa. Si la API externa falló, el servidor
    devuelve un fallback y lo indica en el campo 'fuente_externa'.
    """
    resp = requests.get(f"{BASE_URL}/briefing/{nombre}")
    resp.raise_for_status()
    datos = resp.json()
    print(f"\n[6] === Briefing de {nombre} ===")
    print(f"     Rol            : {datos.get('rol')}")
    print(f"     Energía        : {datos.get('energia')}")
    print(f"     Misiones activas: {datos.get('misiones_activas')} / {datos.get('total_misiones')}")
    print(f"     Consejo externo: {datos.get('consejo_externo')}")
    print(f"     Fuente         : {datos.get('fuente_externa')}")


def enviar_y_leer_mensajes(
    remitente: str, destinatario: str, contenido: str
) -> None:
    """Paso 7: envía un mensaje entre agentes y muestra los últimos
    tres mensajes de la bandeja del destinatario para confirmar que llegó.
    """
    datos = {
        "remitente": remitente,
        "destinatario": destinatario,
        "contenido": contenido,
    }
    resp = requests.post(f"{BASE_URL}/mensajes/", json=datos)
    print(f"\n[7a] Mensaje enviado: {resp.json().get('mensaje', resp.json())}")

    resp = requests.get(f"{BASE_URL}/mensajes/{destinatario}")
    mensajes = resp.json()
    print(f"[7b] Bandeja de {destinatario} ({len(mensajes)} mensajes):")
    for msg in mensajes[-3:]:
        print(f"     [{msg['timestamp'][:19]}] {msg['remitente']} → {msg['contenido']}")


def demo_auth_rechazada() -> None:
    """Paso 8: intenta crear una misión sin enviar el header X-API-KEY.
    Espero un 401 — si el sistema está bien configurado, lo rechaza
    antes de llegar a cualquier lógica de negocio.
    """
    resp = requests.post(
        f"{BASE_URL}/misiones/",
        json={
            "titulo": "Prueba sin auth",
            "agente_asignado": "Atlas",
            "estado": "pendiente",
            "energia_requerida": 5,
        },
    )
    print(
        f"\n[8] Sin X-API-KEY → status={resp.status_code} | {resp.json().get('detail')}"
    )


# ── Guion principal ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 62)
    print("  DEMO: Circuito completo de la Agencia de Agentes")
    print("=" * 62)

    try:
        # 1. Verificar servidor
        verificar_servidor()

        # 2. Crear agente de demostración
        nombre_agente = "Orion"
        crear_agente(nombre_agente, "estratega", 120)

        # 3. Consultar que el agente fue creado correctamente
        agente = consultar_agente_http(nombre_agente)
        print(f"[3] Agente consultado: {agente}")

        # 4. Crear misión asignada a ese agente
        mision_id = crear_mision(
            titulo="Infiltración Sede Central",
            descripcion="Obtener datos del servidor enemigo sin ser detectado.",
            agente=nombre_agente,
            energia_requerida=25,
            prioridad=1,
        )

        # 5. Completar la misión (la clase descuenta energía)
        if mision_id is not None:
            completar_mision(mision_id)

        # 6. Briefing del agente (datos locales + consejo de API externa)
        consultar_briefing(nombre_agente)

        # 7. Enviar mensaje y leer bandeja
        enviar_y_leer_mensajes(
            remitente=nombre_agente,
            destinatario="Atlas",
            contenido="Misión cumplida. Datos asegurados y enviados a base.",
        )

        # 8. Petición sin API key → 401
        demo_auth_rechazada()

        print("\n" + "=" * 62)
        print("  Circuito completo ejecutado sin errores.")
        print("=" * 62)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se puede conectar al servidor.")
        print("Asegúrate de que uvicorn esté corriendo desde la carpeta Reto/:")
        print("    uvicorn main:app --reload")
        sys.exit(1)
