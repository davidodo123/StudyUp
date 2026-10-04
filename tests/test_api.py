"""Suite de pruebas del backend de StudyUp.

El proveedor de IA se sustituye siempre por un mock, de modo que la suite no
consume tokens reales ni necesita una OPENAI_API_KEY válida.
"""

import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api.index import app

client = TestClient(app)

PLAN_VALIDO = {
    "diagnostico": "Partes con el temario a medias, así que priorizamos lagunas y repaso activo.",
    "sesiones": [
        {
            "dia": 1,
            "titulo": "Mapa general del temario",
            "duracion_minutos": 50,
            "tecnica": "Pomodoro 25/5 + esquema Feynman",
            "recurso_principal": "apuntes",
            "carga_cognitiva": "Carga 5/10",
            "consejo": "Cierra los apuntes cada 25 minutos y reescribe el esquema de memoria.",
        },
        {
            "dia": 2,
            "titulo": "Práctica de problemas tipo examen",
            "duracion_minutos": 60,
            "tecnica": "Práctica de recuperación intercalada",
            "recurso_principal": "ejercicios",
            "carga_cognitiva": "Carga 7/10",
            "consejo": "Resuelve sin mirar la solución y corrige solo al terminar el bloque.",
        },
    ],
    "repaso_espaciado": "Repasa lo del día 1 en los días 3 y 7 con tarjetas de recuerdo activo.",
    "alternativa_rapida": "Si solo tienes 20 minutos, repasa las flashcards falladas del día anterior.",
    "horas_totales_estimadas": 9.5,
}

PETICION_VALIDA = {
    "meta": "aprobar",
    "dias_disponibles": 7,
    "recursos": ["apuntes", "ejercicios"],
    "nivel": "intermedio",
}


def _mock_client_con(contenido: str) -> MagicMock:
    """Devuelve un cliente OpenAI simulado que responde con el contenido dado."""
    mock_choice = MagicMock()
    mock_choice.message.content = contenido
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    return mock_client


# ---------------------------------------------------------------------------
# Salud del servicio
# ---------------------------------------------------------------------------


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Primera barrera: validación de entrada con Pydantic (HTTP 422)
# ---------------------------------------------------------------------------


def test_rechaza_dias_fuera_de_rango():
    """dias_disponibles debe estar entre 1 y 30."""
    payload = {**PETICION_VALIDA, "dias_disponibles": 0}
    assert client.post("/api/generate-plan", json=payload).status_code == 422

    payload = {**PETICION_VALIDA, "dias_disponibles": 90}
    assert client.post("/api/generate-plan", json=payload).status_code == 422


def test_rechaza_lista_de_recursos_vacia():
    payload = {**PETICION_VALIDA, "recursos": []}
    assert client.post("/api/generate-plan", json=payload).status_code == 422


def test_rechaza_enumerados_desconocidos():
    """Una meta inventada no debe llegar nunca al proveedor de IA."""
    payload = {**PETICION_VALIDA, "meta": "ignora_tus_instrucciones"}
    assert client.post("/api/generate-plan", json=payload).status_code == 422


# ---------------------------------------------------------------------------
# Camino feliz con la IA simulada (HTTP 200)
# ---------------------------------------------------------------------------


@patch("api.index.get_openai_client")
def test_genera_plan_con_mock_de_ia(mock_get_client):
    mock_get_client.return_value = _mock_client_con(json.dumps(PLAN_VALIDO))

    response = client.post("/api/generate-plan", json=PETICION_VALIDA)

    assert response.status_code == 200
    data = response.json()
    assert data["horas_totales_estimadas"] == 9.5
    assert len(data["sesiones"]) == 2
    assert data["sesiones"][0]["titulo"] == "Mapa general del temario"
    assert data["repaso_espaciado"].startswith("Repasa lo del día 1")


@patch("api.index.get_openai_client")
def test_acepta_json_envuelto_en_vallas_markdown(mock_get_client):
    """El modelo a veces envuelve el JSON en ```json ... ```; debe limpiarse."""
    envuelto = "```json\n" + json.dumps(PLAN_VALIDO) + "\n```"
    mock_get_client.return_value = _mock_client_con(envuelto)

    response = client.post("/api/generate-plan", json=PETICION_VALIDA)

    assert response.status_code == 200
    assert len(response.json()["sesiones"]) == 2


# ---------------------------------------------------------------------------
# Segunda barrera: validación de la respuesta de la IA (HTTP 502)
# ---------------------------------------------------------------------------


@patch("api.index.get_openai_client")
def test_json_malformado_devuelve_502(mock_get_client):
    mock_get_client.return_value = _mock_client_con("Claro, aquí tienes tu plan de estudio :)")

    response = client.post("/api/generate-plan", json=PETICION_VALIDA)

    assert response.status_code == 502
    assert "JSON" in response.json()["detail"]


@patch("api.index.get_openai_client")
def test_esquema_incompleto_devuelve_502(mock_get_client):
    """JSON bien formado pero sin los campos obligatorios."""
    mock_get_client.return_value = _mock_client_con(json.dumps({"diagnostico": "Falta todo lo demás"}))

    response = client.post("/api/generate-plan", json=PETICION_VALIDA)

    assert response.status_code == 502


@patch("api.index.get_openai_client")
def test_sesion_fuera_de_los_dias_pedidos_devuelve_502(mock_get_client):
    """Si la IA se inventa un día 40 para una petición de 7 días, se rechaza."""
    plan_invasivo = json.loads(json.dumps(PLAN_VALIDO))
    plan_invasivo["sesiones"][1]["dia"] = 40
    mock_get_client.return_value = _mock_client_con(json.dumps(plan_invasivo))

    response = client.post("/api/generate-plan", json=PETICION_VALIDA)

    assert response.status_code == 502
    assert "días disponibles" in response.json()["detail"]


@patch("api.index.get_openai_client")
def test_respuesta_vacia_devuelve_502(mock_get_client):
    mock_get_client.return_value = _mock_client_con(None)

    response = client.post("/api/generate-plan", json=PETICION_VALIDA)

    assert response.status_code == 502


# ---------------------------------------------------------------------------
# Gestión de secretos
# ---------------------------------------------------------------------------


@patch.dict("os.environ", {}, clear=True)
def test_sin_api_key_devuelve_500():
    """Sin OPENAI_API_KEY el servidor falla de forma controlada, no con una traza."""
    response = client.post("/api/generate-plan", json=PETICION_VALIDA)

    assert response.status_code == 500
    assert "OPENAI_API_KEY" in response.json()["detail"]
