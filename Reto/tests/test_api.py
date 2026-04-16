"""
tests/test_api.py — Pruebas de la Agencia de Agentes.

Para correr los tests desde la carpeta Reto/:
    pytest tests/ -v
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_crear_mision_sin_api_key_devuelve_401():
    """
    POST /misiones/ sin el header X-API-KEY debe rechazar la petición con 401
    antes de llegar a cualquier lógica de negocio.
    """
    payload = {
        "titulo": "Misión sin auth",
        "agente_asignado": "Atlas",
        "estado": "pendiente",
        "energia_requerida": 10,
    }
    response = client.post("/misiones/", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "API key inválida"


def test_briefing_retorna_estructura_con_datos_locales_y_externos_mockeados():
    """
    GET /briefing/{nombre} debe combinar datos locales del agente con un campo
    traído de la API externa. Mockeamos despertar_agente, listar_misiones_agente
    y requests.get para que el test no dependa de la base de datos real ni de
    internet — solo verificamos que el endpoint arma bien la respuesta.
    """
    agente_en_db = {"nombre": "Atlas", "rol": "explorador", "energia": 100}
    misiones_en_db = [
        {
            "id": 1, "titulo": "Reconocimiento", "descripcion": "",
            "agente_asignado": "Atlas", "estado": "completada",
            "energia_requerida": 20, "prioridad": 2,
            "deadline": None, "recompensa": 10, "created_at": "2026-01-01T00:00:00",
        },
        {
            "id": 2, "titulo": "Vigilancia", "descripcion": "",
            "agente_asignado": "Atlas", "estado": "pendiente",
            "energia_requerida": 15, "prioridad": 3,
            "deadline": None, "recompensa": 5, "created_at": "2026-01-02T00:00:00",
        },
    ]

    # Simulo la respuesta de Advice Slip API
    mock_ext = MagicMock()
    mock_ext.raise_for_status.return_value = None
    mock_ext.json.return_value = {"slip": {"id": 42, "advice": "Consejo de prueba"}}

    with (
        patch("main.despertar_agente", return_value=agente_en_db),
        patch("main.listar_misiones_agente", return_value=misiones_en_db),
        patch("main.requests.get", return_value=mock_ext),
    ):
        response = client.get("/briefing/Atlas")

    assert response.status_code == 200
    datos = response.json()

    # Datos locales del agente
    assert datos["nombre"] == "Atlas"
    assert datos["rol"] == "explorador"
    assert datos["energia"] == 100

    # Métricas calculadas en el endpoint a partir de las misiones
    assert datos["total_misiones"] == 2
    assert datos["misiones_activas"] == 1  # solo "pendiente" cuenta, "completada" no

    # Dato externo
    assert datos["consejo_externo"] == "Consejo de prueba"
    assert datos["fuente_externa"] == "api.adviceslip.com"
