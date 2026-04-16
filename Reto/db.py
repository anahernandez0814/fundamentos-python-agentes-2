import sqlite3
import datetime
import os

# Construyo la ruta absoluta a la base de datos usando la ubicación de este
# archivo, no el directorio desde donde se corre el servidor. Así funciona
# sin importar desde qué carpeta se ejecute uvicorn.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agentes.db")


# ── Inicialización ──────────────────────────────────────────────────────────

def crear_tablas() -> None:
    """Crea las tres tablas si todavía no existen.
    Puedo llamar esto tranquilamente varias veces — IF NOT EXISTS
    se encarga de que no explote si ya están creadas.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agentes (
            nombre  TEXT PRIMARY KEY,
            rol     TEXT,
            energia INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente    TEXT,
            destinatario TEXT,
            contenido    TEXT,
            timestamp    TEXT
        )
    """)

    # La tabla de misiones es nueva en este reto. Agregué tres columnas
    # extra además del mínimo pedido: prioridad para ordenar por urgencia,
    # deadline para misiones con fecha límite, y recompensa para cuando
    # en el futuro queramos que completar misiones devuelva energía al agente.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo            TEXT    NOT NULL,
            descripcion       TEXT,
            agente_asignado   TEXT,
            estado            TEXT,
            energia_requerida INTEGER,
            prioridad         INTEGER DEFAULT 3,
            deadline          TEXT,
            recompensa        INTEGER DEFAULT 0,
            created_at        TEXT
        )
    """)

    conn.commit()
    conn.close()


# ── Agentes ─────────────────────────────────────────────────────────────────

def registrar_agente(nombre: str, rol: str, energia: int) -> str:
    """Inserta un agente nuevo en la base de datos.
    Si el nombre ya existe (es la PRIMARY KEY), SQLite lanza IntegrityError
    y retorno un mensaje de error en vez de dejar que el servidor explote.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO agentes (nombre, rol, energia) VALUES (?, ?, ?)",
            (nombre, rol, energia),
        )
        conn.commit()
        resultado = f"[DB] Agente '{nombre}' registrado con éxito."
    except sqlite3.IntegrityError:
        resultado = f"[DB] Error: El agente '{nombre}' ya existe en la base de datos."
    finally:
        conn.close()
    return resultado


def despertar_agente(nombre: str) -> dict | None:
    """Trae un agente de la base de datos por nombre.
    Retorna un diccionario con sus datos o None si no existe.
    El nombre "despertar" lo tomé de la Semana 5 — la idea es que
    el agente "revive" en memoria cuando lo sacamos del disco.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nombre, rol, energia FROM agentes WHERE nombre = ?", (nombre,)
    )
    fila = cursor.fetchone()
    conn.close()
    if fila is None:
        return None
    return {"nombre": fila[0], "rol": fila[1], "energia": fila[2]}


def actualizar_energia_agente(nombre: str, nueva_energia: int) -> bool:
    """Guarda la energía actualizada del agente después de completar una misión.
    Retorna True si el agente existía y se actualizó correctamente.
    Uso rowcount para verificar — si es 0, es porque el nombre no existe en la tabla.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE agentes SET energia = ? WHERE nombre = ?",
        (nueva_energia, nombre),
    )
    actualizado = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return actualizado


def listar_agentes() -> list[dict]:
    """Devuelve todos los agentes registrados como lista de diccionarios."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia FROM agentes")
    filas = cursor.fetchall()
    conn.close()
    return [{"nombre": f[0], "rol": f[1], "energia": f[2]} for f in filas]


# ── Mensajes ─────────────────────────────────────────────────────────────────

def enviar_mensaje(remitente: str, destinatario: str, contenido: str) -> str:
    """Guarda un mensaje en la base de datos con el timestamp del momento exacto."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO mensajes (remitente, destinatario, contenido, timestamp) VALUES (?, ?, ?, ?)",
        (remitente, destinatario, contenido, timestamp),
    )
    conn.commit()
    conn.close()
    return f"[DB] Mensaje de '{remitente}' a '{destinatario}' enviado."


def leer_mensajes(nombre_agente: str) -> list[dict]:
    """Trae todos los mensajes dirigidos a un agente, del más antiguo al más reciente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT remitente, destinatario, contenido, timestamp
           FROM mensajes
           WHERE destinatario = ?
           ORDER BY timestamp""",
        (nombre_agente,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {"remitente": f[0], "destinatario": f[1], "contenido": f[2], "timestamp": f[3]}
        for f in filas
    ]


# ── Misiones ─────────────────────────────────────────────────────────────────

def crear_mision(
    titulo: str,
    descripcion: str,
    agente_asignado: str,
    estado: str,
    energia_requerida: int,
    prioridad: int = 3,
    deadline: str | None = None,
    recompensa: int = 0,
) -> int:
    """Inserta una misión nueva y retorna el id que le asignó SQLite.
    Necesito ese id para devolverlo en la respuesta del endpoint
    y que el cliente pueda usarlo inmediatamente en el paso siguiente.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.datetime.now().isoformat()
    cursor.execute(
        """INSERT INTO misiones
           (titulo, descripcion, agente_asignado, estado, energia_requerida,
            prioridad, deadline, recompensa, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (titulo, descripcion, agente_asignado, estado, energia_requerida,
         prioridad, deadline, recompensa, created_at),
    )
    mision_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return mision_id


def obtener_mision(mision_id: int) -> dict | None:
    """Busca una misión por su id. Si no existe, retorna None
    para que el endpoint pueda responder con 404.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, titulo, descripcion, agente_asignado, estado,
                  energia_requerida, prioridad, deadline, recompensa, created_at
           FROM misiones WHERE id = ?""",
        (mision_id,),
    )
    fila = cursor.fetchone()
    conn.close()
    if fila is None:
        return None
    return {
        "id": fila[0],
        "titulo": fila[1],
        "descripcion": fila[2],
        "agente_asignado": fila[3],
        "estado": fila[4],
        "energia_requerida": fila[5],
        "prioridad": fila[6],
        "deadline": fila[7],
        "recompensa": fila[8],
        "created_at": fila[9],
    }


def listar_misiones_agente(nombre_agente: str) -> list[dict]:
    """Trae todas las misiones de un agente ordenadas por fecha de creación."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, titulo, descripcion, agente_asignado, estado,
                  energia_requerida, prioridad, deadline, recompensa, created_at
           FROM misiones
           WHERE agente_asignado = ?
           ORDER BY created_at""",
        (nombre_agente,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {
            "id": f[0],
            "titulo": f[1],
            "descripcion": f[2],
            "agente_asignado": f[3],
            "estado": f[4],
            "energia_requerida": f[5],
            "prioridad": f[6],
            "deadline": f[7],
            "recompensa": f[8],
            "created_at": f[9],
        }
        for f in filas
    ]


def actualizar_estado_mision(mision_id: int, estado: str) -> bool:
    """Cambia el estado de una misión. Retorna True si la misión existía."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE misiones SET estado = ? WHERE id = ?",
        (estado, mision_id),
    )
    actualizado = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return actualizado


# ── Datos semilla ─────────────────────────────────────────────────────────────

def seed_if_empty() -> None:
    """Puebla la base de datos con datos de prueba la primera vez que arranca el servidor.
    Antes de insertar nada, reviso si ya hay agentes — si los hay, no hago nada.
    Así no duplico datos si el servidor se reinicia.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agentes")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    ts = datetime.datetime.now().isoformat()

    # Tres agentes en roles distintos: uno normal, uno admin y uno guardián.
    # Los elegí así para poder probar la reconstrucción de clases en el endpoint
    # de completar misiones — Nova es admin, así que isinstance devuelve True para ella.
    cursor.executemany(
        "INSERT INTO agentes (nombre, rol, energia) VALUES (?, ?, ?)",
        [
            ("Atlas", "explorador", 100),
            ("Nova", "admin", 150),
            ("Titan", "guardian", 200),
        ],
    )

    # Cinco mensajes cruzados entre los agentes para tener bandejas con contenido.
    cursor.executemany(
        "INSERT INTO mensajes (remitente, destinatario, contenido, timestamp) VALUES (?, ?, ?, ?)",
        [
            ("Atlas", "Nova", "Encontré un artefacto en la cueva norte.", ts),
            ("Nova", "Atlas", "Excelente. Enviaré un dron de análisis.", ts),
            ("Titan", "Nova", "Perímetro asegurado. Sin amenazas detectadas.", ts),
            ("Atlas", "Titan", "Necesito apoyo en el sector este.", ts),
            ("Nova", "Titan", "Confirma situación en la zona sur.", ts),
        ],
    )

    # Tres misiones en estados distintos para cumplir el requisito del reto
    # y para que haya variedad al explorar la API desde Swagger.
    # Ojo: la misión 1 ya viene "completada" — si intentas completarla de nuevo
    # el servidor responde 400, que es el comportamiento correcto.
    cursor.executemany(
        """INSERT INTO misiones
           (titulo, descripcion, agente_asignado, estado, energia_requerida,
            prioridad, deadline, recompensa, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                "Reconocimiento Zona Norte",
                "Explorar el sector norte y reportar hallazgos.",
                "Atlas", "completada", 20, 2, None, 10, ts,
            ),
            (
                "Análisis de Artefacto",
                "Analizar el artefacto encontrado por Atlas.",
                "Nova", "en_curso", 30, 1, None, 25, ts,
            ),
            (
                "Patrulla Perimetral",
                "Mantener vigilancia del perímetro sur.",
                "Titan", "pendiente", 15, 3, None, 5, ts,
            ),
        ],
    )

    conn.commit()
    conn.close()
