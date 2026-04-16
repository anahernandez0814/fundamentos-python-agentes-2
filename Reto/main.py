import logging

import requests
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from agente import AgenteAdmin, PseudoAgente
from config import AGENCIA_API_KEY, EXTERNAL_API_URL
from db import (
    actualizar_energia_agente,
    actualizar_estado_mision,
    crear_mision,
    crear_tablas,
    despertar_agente,
    enviar_mensaje,
    leer_mensajes,
    listar_agentes,
    listar_misiones_agente,
    obtener_mision,
    registrar_agente,
    seed_if_empty,
)

# Configuré el logger con nivel INFO porque no quiero ver el ruido de DEBUG
# en ejecución normal. WARNING lo reservo para cuando algo raro pasa pero
# el sistema sigue funcionando (API externa caída, key incorrecta).
# ERROR queda para fallos reales que necesitan atención inmediata.
# El formato con fecha y nivel en cada línea hace que los logs sean
# legibles aunque los veas horas después fuera de contexto.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Al arrancar el servidor me aseguro de que las tablas existan
# y de que haya datos semilla si es la primera vez.
crear_tablas()
seed_if_empty()


# ── Modelos Pydantic ──────────────────────────────────────────────────────────
# Estos modelos le dicen a FastAPI qué forma tienen los datos que acepta cada
# endpoint.

class AgenteRequest(BaseModel):
    nombre: str
    rol: str
    energia: int = 100


class MensajeRequest(BaseModel):
    remitente: str
    destinatario: str
    contenido: str


class MisionRequest(BaseModel):
    titulo: str
    descripcion: str = ""
    agente_asignado: str
    estado: str = "pendiente"
    energia_requerida: int
    prioridad: int = 3
    deadline: str | None = None
    recompensa: int = 0


# ── Aplicación ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agencia de Agentes",
    description=(
        "API para gestionar agentes autónomos, misiones y comunicaciones. "
        "Los endpoints de escritura requieren el header X-API-KEY."
    ),
    version="1.0.0",
)


# ── Autenticación ─────────────────────────────────────────────────────────────
# Decidí proteger solo los endpoints que modifican datos: crear agentes,
# crear misiones y completar misiones. Los GET los dejé públicos porque
# consultar información no tiene efecto secundario y facilita que otras
# herramientas puedan monitorear la agencia sin necesidad de credenciales.
#
# Uso default=None en el Header para que cuando no venga la key el servidor
# responda 401 y no 422. Con Header(...) obligatorio FastAPI falla antes de
# llegar a esta función y el cliente recibe un error de validación en vez
# de el "API key inválida" que tiene más sentido en este contexto.
def verificar_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Revisa que el header X-API-KEY exista y coincida con el valor del .env.
    Si no viene o es incorrecto, corto el request con 401 antes de que llegue
    al endpoint. Registro un warning para saber si alguien está intentando
    acceder sin autorización.
    """
    if x_api_key is None or x_api_key != AGENCIA_API_KEY:
        logger.warning("Intento de acceso con API key inválida o ausente.")
        raise HTTPException(status_code=401, detail="API key inválida")


# ── Endpoints de la Semana 5 (conservados) ───────────────────────────────────

@app.get("/")
def inicio():
    return {"status": "online", "mensaje": "Agencia de Agentes activa y operando"}


@app.get("/agentes/")
def obtener_todos_los_agentes():
    return listar_agentes()


@app.post("/agentes/", dependencies=[Depends(verificar_api_key)])
def crear_agente(agente: AgenteRequest):
    resultado = registrar_agente(agente.nombre, agente.rol, agente.energia)
    logger.info(f"Agente creado: nombre={agente.nombre} | rol={agente.rol}")
    return {"mensaje": resultado}


@app.get("/agente/{nombre}")
def obtener_agente(nombre: str):
    agente = despertar_agente(nombre)
    if agente is None:
        raise HTTPException(status_code=404, detail=f"Agente '{nombre}' no encontrado")
    return agente


@app.post("/mensajes/")
def crear_mensaje(mensaje: MensajeRequest):
    resultado = enviar_mensaje(mensaje.remitente, mensaje.destinatario, mensaje.contenido)
    logger.info(f"Mensaje enviado: {mensaje.remitente} -> {mensaje.destinatario}")
    return {"mensaje": resultado}


@app.get("/mensajes/{nombre}")
def obtener_mensajes(nombre: str):
    return leer_mensajes(nombre)


# ── Endpoints de misiones (nuevos en el reto) ─────────────────────────────────

@app.post("/misiones/", dependencies=[Depends(verificar_api_key)])
def crear_mision_endpoint(mision: MisionRequest):
    # Antes de crear la misión, verifico que el agente asignado exista.
    # No tiene sentido guardar una misión huérfana en la base de datos.
    if despertar_agente(mision.agente_asignado) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agente '{mision.agente_asignado}' no encontrado",
        )

    mision_id = crear_mision(
        titulo=mision.titulo,
        descripcion=mision.descripcion,
        agente_asignado=mision.agente_asignado,
        estado=mision.estado,
        energia_requerida=mision.energia_requerida,
        prioridad=mision.prioridad,
        deadline=mision.deadline,
        recompensa=mision.recompensa,
    )
    logger.info(
        f"Misión creada: id={mision_id} | '{mision.titulo}' | agente={mision.agente_asignado}"
    )
    return {"id": mision_id, "mensaje": f"Misión '{mision.titulo}' creada con éxito."}


@app.get("/misiones/{id}")
def obtener_mision_endpoint(id: int):
    mision = obtener_mision(id)
    if mision is None:
        raise HTTPException(status_code=404, detail=f"Misión con id={id} no encontrada")
    return mision


@app.get("/agente/{nombre}/misiones")
def misiones_de_agente(nombre: str):
    if despertar_agente(nombre) is None:
        raise HTTPException(status_code=404, detail=f"Agente '{nombre}' no encontrado")
    return listar_misiones_agente(nombre)


@app.post("/misiones/{id}/completar", dependencies=[Depends(verificar_api_key)])
def completar_mision_endpoint(id: int):
    # Primero verifico que la misión exista y que no esté ya completada.
    mision = obtener_mision(id)
    if mision is None:
        raise HTTPException(status_code=404, detail=f"Misión con id={id} no encontrada")

    if mision["estado"] == "completada":
        raise HTTPException(status_code=400, detail="La misión ya está completada")

    # Traigo el agente de la DB y reconstruyo el objeto con su clase correcta.
    # Si es admin instancio AgenteAdmin, si no PseudoAgente.
    # Esto es lo que garantiza que isinstance(agente, AgenteAdmin) funcione
    # correctamente y que la lógica de negocio viva en la clase, no acá.
    datos = despertar_agente(mision["agente_asignado"])
    if datos is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agente '{mision['agente_asignado']}' no encontrado",
        )

    if datos["rol"] == "admin":
        agente: PseudoAgente = AgenteAdmin(
            name=datos["nombre"], rol=datos["rol"], energia=datos["energia"]
        )
    else:
        agente = PseudoAgente(
            name=datos["nombre"], rol=datos["rol"], energia=datos["energia"]
        )

    # Le pregunto a la clase si puede completar la misión — ella decide,
    # no yo. Si retorna False es porque la energía no alcanza.
    exito = agente.completar_mision(mision["energia_requerida"])
    if not exito:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Energía insuficiente. El agente tiene {agente.energia} "
                f"pero la misión requiere {mision['energia_requerida']}."
            ),
        )

    # Si todo salió bien, persisto los cambios: nuevo estado de la misión
    # y nueva energía del agente en la base de datos.
    actualizar_estado_mision(id, "completada")
    actualizar_energia_agente(agente.name, agente.energia)

    logger.info(
        f"Misión completada: id={id} | agente={agente.name} | "
        f"energia_restante={agente.energia} | es_admin={isinstance(agente, AgenteAdmin)}"
    )
    return {
        "mensaje": f"Misión '{mision['titulo']}' completada con éxito.",
        "agente": agente.name,
        "energia_restante": agente.energia,
        "es_admin": isinstance(agente, AgenteAdmin),
    }


# ── Briefing con API externa ──────────────────────────────────────────────────
# Elegí Advice Slip API (https://api.adviceslip.com/advice) porque encaja
# con la narrativa: cada briefing de campo termina con una lección aprendida.
# La API es gratuita, sin registro, sin límites documentados, y responde rápido.
#
# Mi plan si falla: timeout de 5 segundos y un try/except que captura cualquier
# excepción. Si algo sale mal, el servidor no se cae — responde igual pero con
# un consejo local de fallback y registra un warning.
@app.get("/briefing/{nombre}")
def briefing_agente(nombre: str):
    datos = despertar_agente(nombre)
    if datos is None:
        raise HTTPException(status_code=404, detail=f"Agente '{nombre}' no encontrado")

    misiones = listar_misiones_agente(nombre)
    misiones_activas = [m for m in misiones if m["estado"] != "completada"]

    try:
        respuesta_ext = requests.get(
            EXTERNAL_API_URL,
            timeout=5,
            headers={"Accept": "application/json"},
        )
        respuesta_ext.raise_for_status()
        consejo = respuesta_ext.json()["slip"]["advice"]
        fuente_externa = "api.adviceslip.com"
        logger.info(f"Briefing generado para '{nombre}' con dato externo.")
    except requests.exceptions.Timeout:
        logger.warning(
            f"Timeout al consultar API externa para briefing de '{nombre}'. Usando fallback."
        )
        consejo = "La paciencia y la precisión son las armas más poderosas de un agente."
        fuente_externa = "fallback_local"
    except Exception as e:
        logger.warning(
            f"API externa falló para briefing de '{nombre}': {e}. Usando fallback."
        )
        consejo = "La paciencia y la precisión son las armas más poderosas de un agente."
        fuente_externa = "fallback_local"

    return {
        **datos,
        "misiones_activas": len(misiones_activas),
        "total_misiones": len(misiones),
        "consejo_externo": consejo,
        "fuente_externa": fuente_externa,
    }
