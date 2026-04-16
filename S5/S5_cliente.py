# -----------------------------------------------------------#
# Semana 5 - Sesion 2 (Capitulos 6-7): Cliente HTTP
# -----------------------------------------------------------#
# Este script es el CLIENTE que se comunica con el servidor
# FastAPI (S5_sesion_2.py). Debes ejecutarlo en una TERMINAL
# SEPARADA mientras el servidor esta corriendo.
#
# Requisitos:
# 1. Instala requests (solo la primera vez):
#       pip install requests
# 2. En otra terminal, el servidor debe estar corriendo:
#       cd S5
#       uvicorn S5_sesion_2:app --reload
# 3. Ejecuta este script:
#       python S5_cliente.py
# -----------------------------------------------------------#

import requests

BASE_URL = "http://localhost:8000"


# ======================================================
# CAPITULO 6: El agente como cliente HTTP (10 min)
# ======================================================
# Hasta ahora hemos probado nuestro servidor desde Swagger UI
# (el navegador). Pero el objetivo real es que OTROS PROGRAMAS
# se comuniquen con nuestros agentes.
#
# La libreria `requests` permite hacer peticiones HTTP desde
# Python. Es como tener un navegador invisible dentro de tu
# codigo.
#
# Conceptos clave:
# - requests.get(url)   -> peticion GET (leer datos)
# - requests.post(url)  -> peticion POST (enviar datos)
# - respuesta.status_code -> codigo HTTP (200, 404, 500...)
# - respuesta.json()    -> convierte la respuesta JSON a dict
# - json=datos          -> envia un diccionario como JSON en
#                          el body de la peticion POST
#
# Ahora el agente habla por HTTP, no por llamada directa a
# funcion. Es el mismo resultado, pero ahora podria estar
# en otra maquina.
# ======================================================

# --- Descomenta las siguientes funciones ---

def consultar_agente_http(nombre: str) -> dict | None:
    """Consulta un agente a traves del API usando requests.get()."""
    respuesta = requests.get(f"{BASE_URL}/agente/{nombre}")
    if respuesta.status_code == 200:
        return respuesta.json()
    elif respuesta.status_code == 404:
        print(f"[Cliente] Agente '{nombre}' no encontrado (404)")
        return None
    else:
        print(f"[Cliente] Error inesperado: {respuesta.status_code}")
        return None


def enviar_mensaje_http(remitente: str, destinatario: str, contenido: str) -> dict:
    """Envia un mensaje a traves del API usando requests.post()."""
    datos = {"remitente": remitente, "destinatario": destinatario, "contenido": contenido}
    respuesta = requests.post(f"{BASE_URL}/mensajes/", json=datos)
    return respuesta.json()

# PRUEBA: Descomenta las funciones de arriba. Luego envia un mensaje via HTTP
#         ejecutando este script. Despues abre Swagger UI (http://localhost:8000/docs)
#         y consulta la bandeja con GET /mensajes/{nombre}. ¿El mensaje aparece?
# CONCLUSION: Ejecute el script y envie un mensaje de prueba con requests.post().
#         Despues abri Swagger UI, consulte GET /mensajes/Atlas y ahi estaba el
#         mensaje que mande desde Python. Tiene sentido porque ambos llegan al
#         mismo servidor y a la misma base de datos.


# ======================================================
# CAPITULO 7: El circuito completo (10 min)
# ======================================================
# Ahora vamos a juntar todo: verificar el servidor, crear un
# agente, consultarlo, enviar un mensaje y leer la bandeja.
# Todo desde Python, sin tocar el navegador.
#
# Este es el patron real de comunicacion entre sistemas:
# un programa envia peticiones HTTP a otro. Asi funcionan
# las apps de tu telefono, los chatbots, los microservicios...
# ======================================================

# --- Descomenta el siguiente bloque ---

if __name__ == "__main__":
    # 1. Verificar que el servidor esta activo
    respuesta = requests.get(f"{BASE_URL}/")
    print(f"Servidor: {respuesta.json()}")

    # 2. Registrar un agente via POST
    nuevo_agente = {"nombre": "Orion", "rol": "estratega", "energia": 130}
    respuesta = requests.post(f"{BASE_URL}/agentes/", json=nuevo_agente)
    print(f"Registrar agente: {respuesta.json()}")

    # 3. Consultar el agente via GET
    agente = consultar_agente_http("Orion")
    print(f"Agente consultado: {agente}")

    # 4. Enviar un mensaje via POST
    resultado = enviar_mensaje_http("Orion", "Atlas", "Solicito reporte de la mision.")
    print(f"Mensaje enviado: {resultado}")

    # 5. Consultar bandeja de Atlas via GET
    respuesta = requests.get(f"{BASE_URL}/mensajes/Atlas")
    mensajes = respuesta.json()
    print(f"\n--- Bandeja de Atlas ({len(mensajes)} mensajes) ---")
    for msg in mensajes:
        print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}")

# PRUEBA: Descomenta todo el bloque de arriba y ejecuta este script.
#         Luego abre Swagger UI y haz lo mismo manualmente desde el navegador.
#         ¿Ves los mismos datos? Ambos caminos llegan al mismo servidor.
# CONCLUSION: Descomente el bloque, lo ejecute y vi como registro a Orion, lo
#         consulto, envio un mensaje y leyo la bandeja, todo desde la terminal.
#         Despues hice lo mismo en Swagger UI y los datos eran iguales. Es logico
#         porque tanto el script como el navegador mandan peticiones HTTP al mismo
#         servidor.


# -----------------------------------------------------------#
# Felicidades! Completaste el circuito cliente-servidor.
#
# Resumen de lo aprendido:
# - requests.get(): leer datos del servidor (como GET en Swagger)
# - requests.post(): enviar datos al servidor (como POST en Swagger)
# - response.status_code: verificar si la peticion fue exitosa
# - response.json(): convertir la respuesta a diccionario Python
# - json=datos: enviar un diccionario como JSON en el body
#
# Lo importante: tu script de Python y Swagger UI hacen EXACTAMENTE
# lo mismo. Ambos envian peticiones HTTP al servidor. La unica
# diferencia es la interfaz: codigo vs navegador.
# -----------------------------------------------------------#
