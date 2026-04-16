# -----------------------------------------------------------#
# Semana 5 - Sesion 1: Persistencia con SQLite
# -----------------------------------------------------------#
# Hasta ahora, cada vez que cierras Python, todo desaparece.
# Los agentes, los mensajes, los datos... se pierden en la RAM.
# Hoy aprenderemos a darle MEMORIA PERMANENTE a nuestros agentes
# usando SQLite: una base de datos que vive en un solo archivo.
#
# Instrucciones:
# 1. Lee cada capitulo de arriba hacia abajo
# 2. Descomenta el bloque de codigo indicado
# 3. Ejecuta el script completo: python S5_sesion_1.py
# 4. Observa la salida, experimenta, y escribe tu CONCLUSION
# 5. Avanza al siguiente capitulo
# -----------------------------------------------------------#

import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agentes.db")

# -----------------------------------------------------------#
# SECCION A: Funciones del modulo (siempre disponibles)
# -----------------------------------------------------------#
# Estas funciones NO estan comentadas porque otros archivos
# las importan. No las modifiques a menos que se indique.
# -----------------------------------------------------------#


def crear_tablas() -> None:
    """Crea las tablas agentes y mensajes si no existen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agentes (
            nombre TEXT PRIMARY KEY,
            rol TEXT,
            energia INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT,
            destinatario TEXT,
            contenido TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def registrar_agente(nombre: str, rol: str, energia: int) -> str:
    """Registra un agente en la base de datos. Retorna mensaje de exito o error."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO agentes (nombre, rol, energia) VALUES (?, ?, ?)",
            (nombre, rol, energia),
        )
        conn.commit()
        resultado = f"[DB] Agente '{nombre}' registrado con exito."
    except sqlite3.IntegrityError:
        resultado = f"[DB] Error: El agente '{nombre}' ya existe en la base de datos."
    finally:
        conn.close()
    return resultado


def despertar_agente(nombre: str) -> dict | None:
    """Busca un agente por nombre. Retorna dict o None si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia FROM agentes WHERE nombre = ?", (nombre,))
    fila = cursor.fetchone()
    conn.close()
    if fila is None:
        return None
    return {"nombre": fila[0], "rol": fila[1], "energia": fila[2]}


def enviar_mensaje(remitente: str, destinatario: str, contenido: str) -> str:
    """Inserta un mensaje en la tabla mensajes con timestamp automatico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO mensajes (remitente, destinatario, contenido, timestamp) VALUES (?, ?, ?, ?)",
        (remitente, destinatario, contenido, timestamp),
    )
    conn.commit()
    conn.close()
    return f"[DB] Mensaje de '{remitente}' a '{destinatario}' enviado a las {timestamp}."


def leer_mensajes(nombre_agente: str) -> list[dict]:
    """Lee todos los mensajes dirigidos a un agente, ordenados por timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT remitente, destinatario, contenido, timestamp FROM mensajes WHERE destinatario = ? ORDER BY timestamp",
        (nombre_agente,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {"remitente": f[0], "destinatario": f[1], "contenido": f[2], "timestamp": f[3]}
        for f in filas
    ]


def listar_agentes() -> list[dict]:
    """Retorna una lista con todos los agentes registrados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia FROM agentes")
    filas = cursor.fetchall()
    conn.close()
    return [
        {"nombre": f[0], "rol": f[1], "energia": f[2]}
        for f in filas
    ]


# -----------------------------------------------------------#
# SECCION B: Ejercicios guiados (descomenta capitulo a capitulo)
# -----------------------------------------------------------#

if __name__ == "__main__":

    # ======================================================
    # CAPITULO 1: El problema de la amnesia (5 min)
    # ======================================================
    # Cada vez que ejecutas un script de Python, las variables
    # viven en la RAM. Cuando el script termina, la RAM se libera
    # y todo desaparece. Observa:

    """ agente = {"nombre": "Atlas", "rol": "explorador", "energia": 100}
    print(f"Agente creado: {agente}")
    print("Script terminado. ¿Donde quedo el agente Atlas? En ningun lado. La RAM se borro.") """

    # PRUEBA: Vuelve a ejecutar el script. Atlas nace de cero cada vez. Eso es amnesia.
    # CONCLUSION: Las variables solo viven mientras el script se ejecuta. 
    # Al cerrar Python, todo lo que estaba en RAM desaparece y el agente se pierde por completo.

    # ======================================================
    # CAPITULO 2: SQL en 5 minutos (10 min)
    # ======================================================
    # SQLite es una base de datos que vive en UN SOLO ARCHIVO.
    # No necesitas instalar nada: Python ya lo trae incluido.
    # CREATE TABLE IF NOT EXISTS crea la tabla solo si no existe.
    # Esto significa que puedes ejecutar este codigo muchas veces
    # sin que se rompa nada.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    """ crear_tablas()
    print(f"[Sistema] Tablas creadas. ¿Existe el archivo? {os.path.exists(DB_PATH)}")
    print(f"[Sistema] Archivo de base de datos: {DB_PATH}") """

    # PRUEBA: Busca el archivo agentes.db en tu carpeta S5/. Abrelo con un editor de texto. ¿Que ves? (Nada legible, es binario.)
    # CONCLUSION: SQLite crea un archivo .db en disco que guarda los datos de forma permanente. 
    # No necesita instalacion extra porque Python ya lo incluye. 
    # El archivo es binario, no se lee como texto plano.
    # Inicialmente esta vacio, pero a medida que registres agentes y envies mensajes, 
    # se llenara con la informacion que persiste entre ejecuciones.

    # ======================================================
    # CAPITULO 3: Registrar un agente (10 min)
    # ======================================================
    # INSERT INTO agentes ... inserta una fila nueva.
    # El ? es un PARAMETRO: SQLite reemplaza cada ? por el valor
    # correspondiente de la tupla. NUNCA uses f-strings en SQL
    # porque es vulnerable a inyeccion SQL.
    # Si el nombre ya existe (PRIMARY KEY), salta IntegrityError.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    """ print(registrar_agente("Atlas", "explorador", 100))
    print(registrar_agente("Nova", "cientifica", 150))
    print(registrar_agente("Titan", "guardian", 200)) """

    # PRUEBA: Intenta registrar 'Atlas' dos veces. ¿Que mensaje recibes? ¿Por que?
    # CONCLUSION: La PRIMARY KEY impide duplicados. 
    # Si intento registrar un agente que ya existe, 
    # SQLite lanza un IntegrityError y el programa lo maneja mostrando un 
    # mensaje de error en vez de romperse "Error: El agente {nombre} ya existe en la base de datos.".

    # ======================================================
    # CAPITULO 4: Despertar un agente (10 min)
    # ======================================================
    # SELECT busca datos en la tabla. fetchone() retorna UNA fila
    # como tupla, o None si no hay resultados.
    # Convertimos la tupla a dict para que sea mas facil de usar.
    # Lo importante: los datos PERSISTEN entre ejecuciones.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    datos_atlas = despertar_agente("Atlas")
    print(f"Agente encontrado: {datos_atlas}")
    print("Ahora cierra Python (Ctrl+C o cierra la terminal).")
    print("Vuelve a abrir y ejecuta SOLO este capitulo. El agente sigue ahi.")
    
    datos_fantasma = despertar_agente("NoExisto")
    print(f"Agente inexistente: {datos_fantasma}")

    # PRUEBA: Cierra Python completamente. Vuelve a abrir. Ejecuta despertar_agente('Atlas'). ¿Sigue vivo?
    # CONCLUSION: Los datos persisten entre ejecuciones. 
    # Aunque cierre Python y vuelva a abrirlo, 
    # el agente sigue guardado en el archivo .db. 

    # ======================================================
    # CAPITULO 5: La tabla de mensajes (10 min)
    # ======================================================
    # La tabla mensajes tiene un id autoincrementable: cada mensaje
    # recibe un numero unico automaticamente. El timestamp se genera
    # con datetime.now().isoformat() al momento de enviar.
    # Esto permite tener un historial ordenado de comunicaciones.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    """ print(enviar_mensaje("Atlas", "Nova", "Encontre un artefacto en la cueva norte."))
    print(enviar_mensaje("Nova", "Atlas", "Excelente. Enviare un drone de analisis."))
    print(enviar_mensaje("Titan", "Nova", "Perimetro asegurado. Sin amenazas detectadas.")) """

    # PRUEBA: Envia un mensaje de Atlas a si mismo. ¿Funciona? ¿Deberia?
    # CONCLUSION: Si funciona, porque la tabla no tiene restriccion que lo impida. 
    # El id autoincremental asegura que cada mensaje sea unico y el timestamp registra 
    # el momento exacto del envio.

    # ======================================================
    # CAPITULO 6: Bandeja de entrada (10 min)
    # ======================================================
    # SELECT ... WHERE destinatario = ? filtra los mensajes
    # dirigidos a un agente especifico. ORDER BY timestamp los
    # ordena cronologicamente. fetchall() retorna TODAS las filas.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    """ mensajes_nova = leer_mensajes("Nova")
    print(f"\n--- Bandeja de entrada de Nova ({len(mensajes_nova)} mensajes) ---")
    for msg in mensajes_nova:
        print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}") """

    # PRUEBA: Crea un tercer agente 'Hermes'. Envia mensajes desde Atlas y Nova a Hermes. Lee la bandeja de Hermes.
    """ print(registrar_agente("Hermes", "mensajero", 120))
    print(enviar_mensaje("Atlas", "Hermes", "Necesito que explores el sector este."))
    print(enviar_mensaje("Nova", "Hermes", "Te envio los datos del analisis."))

    mensajes_hermes = leer_mensajes("Hermes")
    print(f"\n--- Bandeja de entrada de Hermes ({len(mensajes_hermes)} mensajes) ---")
    for msg in mensajes_hermes:
        print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}") """

    # CONCLUSION: Con WHERE y ORDER BY puedo filtrar mensajes por destinatario y ordenarlos por fecha.
    # Esto permite que cada agente tenga su propia bandeja de entrada organizada cronologicamente.

    # ======================================================
    # CAPITULO 7: Experimentacion libre (5 min)
    # ======================================================
    # Ahora que conoces las funciones, crea tu propio escenario.
    # Aqui tienes un mini-script de ejemplo que combina todo:

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    crear_tablas()
    print(registrar_agente("Hermes", "mensajero", 120))
    print(registrar_agente("Lyra", "diplomata", 90))
    
    print(enviar_mensaje("Hermes", "Lyra", "Tienes un mensaje del consejo."))
    print(enviar_mensaje("Lyra", "Hermes", "Recibido. Preparare la respuesta."))
    print(enviar_mensaje("Atlas", "Hermes", "Necesito que lleves esto a Lyra."))
    
    print("\n--- Todos los agentes registrados ---")
    for agente in listar_agentes():
        print(f"  {agente['nombre']} | Rol: {agente['rol']} | Energia: {agente['energia']}")
    
    print("\n--- Bandeja de Hermes ---")
    for msg in leer_mensajes("Hermes"):
        print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}")

    # --- Escenario extra: cadena de mensajes entre agentes ---
    print(enviar_mensaje("Nova", "Lyra", "Lyra, necesito que traduzcas este informe."))
    print(enviar_mensaje("Lyra", "Nova", "Listo. Te lo envio en 5 minutos."))
    print(enviar_mensaje("Titan", "Atlas", "Atlas, zona norte despejada. Puedes avanzar."))
    print(enviar_mensaje("Atlas", "Titan", "Recibido. Me muevo ahora."))

    # --- Revisamos las bandejas de todos los agentes ---
    for nombre in ["Atlas", "Nova", "Titan", "Lyra", "Hermes"]:
        mensajes = leer_mensajes(nombre)
        print(f"\n--- Bandeja de {nombre} ({len(mensajes)} mensajes) ---")
        for msg in mensajes:
            print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}")

    # --- Despertamos un agente para verificar persistencia ---
    print("\n--- Verificacion de persistencia ---")
    for nombre in ["Atlas", "Lyra", "Titan"]:
        datos = despertar_agente(nombre)
        if datos:
            print(f"  {datos['nombre']} sigue vivo | Rol: {datos['rol']} | Energia: {datos['energia']}")
        else:
            print(f"  {nombre} no encontrado en la base de datos.")

    # PRUEBA: Cierra Python. Vuelve a abrir. ¿Siguen los mensajes? ¿Y los agentes?
    # CONCLUSION: Todo persiste: tanto agentes como mensajes sobreviven al cierre de Python. SQLite guarda todo en el archivo .db y se puede consultar en cualquier momento sin perder nada.

    # -----------------------------------------------------------#
    # Felicidades! Ya sabes persistir datos con SQLite.
    # En la proxima sesion conectaremos estas funciones a una API
    # web con FastAPI para que otros programas puedan hablar con
    # nuestros agentes a traves de HTTP.
    # -----------------------------------------------------------#
