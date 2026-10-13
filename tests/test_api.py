"""Suite de pruebas del backend de StudyUp.

El proveedor de IA se sustituye siempre por un mock, de modo que la suite no
consume tokens reales ni necesita una OPENAI_API_KEY válida. Los tokens de Clerk
se firman con una clave RSA generada aquí, así que tampoco hace falta red.
"""

import base64
import json
import time
from unittest.mock import MagicMock, patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from api.index import app, clerk_issuer, get_current_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def usuario_autenticado():
    """Por defecto los tests asumen una sesión válida; los de Clerk la quitan."""
    app.dependency_overrides[get_current_user] = lambda: "user_test"
    yield
    app.dependency_overrides.clear()

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


# ---------------------------------------------------------------------------
# Autenticación con Clerk (HTTP 401): ningún rechazo debe llegar a la IA
# ---------------------------------------------------------------------------

DOMINIO_CLERK = "studyup-test.clerk.accounts.dev"
ISSUER = f"https://{DOMINIO_CLERK}"
CLAVE_PUBLICABLE = "pk_test_" + base64.b64encode(f"{DOMINIO_CLERK}$".encode()).decode()
CLAVE_CLERK = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTRA_CLAVE = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _token(clave=CLAVE_CLERK, **cambios) -> str:
    """Firma un token con la forma de un token de sesión de Clerk."""
    ahora = int(time.time())
    claims = {
        "sub": "user_123",
        "iss": ISSUER,
        "iat": ahora,
        "nbf": ahora,
        "exp": ahora + 60,
        "azp": "http://localhost:5173",
        **cambios,
    }
    return jwt.encode(claims, clave, algorithm="RS256", headers={"kid": "clave-test"})


@pytest.fixture
def clerk_real():
    """Quita la sesión simulada y sirve la clave pública de prueba como JWKS."""
    app.dependency_overrides.clear()
    jwks = MagicMock()
    jwks.get_signing_key_from_jwt.return_value = MagicMock(key=CLAVE_CLERK.public_key())
    with patch.dict("os.environ", {"VITE_CLERK_PUBLISHABLE_KEY": CLAVE_PUBLICABLE}), patch(
        "api.index.jwks_client", return_value=jwks
    ), patch("api.index.get_openai_client") as mock_get_client:
        mock_get_client.return_value = _mock_client_con(json.dumps(PLAN_VALIDO))
        yield mock_get_client


def _pedir(token: str | None):
    cabeceras = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post("/api/generate-plan", json=PETICION_VALIDA, headers=cabeceras)


def test_el_emisor_se_deduce_de_la_clave_publicable():
    with patch.dict("os.environ", {"VITE_CLERK_PUBLISHABLE_KEY": CLAVE_PUBLICABLE}):
        assert clerk_issuer() == ISSUER


def test_token_valido_genera_el_plan(clerk_real):
    response = _pedir(_token())

    assert response.status_code == 200
    clerk_real.assert_called_once()


def test_sin_token_devuelve_401(clerk_real):
    response = _pedir(None)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    clerk_real.assert_not_called()


@pytest.mark.parametrize(
    "token",
    [
        "esto-no-es-un-jwt",
        _token(clave=OTRA_CLAVE),
        _token(iss="https://otro-proyecto.clerk.accounts.dev"),
        _token(azp="https://web-ajena.example"),
        jwt.encode({"sub": "user_123", "iss": ISSUER}, "s" * 32, algorithm="HS256"),
    ],
    ids=["mal_formado", "firma_ajena", "otro_emisor", "origen_no_autorizado", "algoritmo_hs256"],
)
def test_token_invalido_devuelve_401(clerk_real, token):
    response = _pedir(token)

    assert response.status_code == 401
    clerk_real.assert_not_called()


def test_token_caducado_devuelve_401(clerk_real):
    hace_una_hora = int(time.time()) - 3600
    response = _pedir(_token(iat=hace_una_hora, nbf=hace_una_hora, exp=hace_una_hora + 60))

    assert response.status_code == 401
    assert "caducado" in response.json()["detail"]
    clerk_real.assert_not_called()


def test_sin_clave_de_clerk_devuelve_500(clerk_real):
    with patch.dict("os.environ", {}, clear=True):
        response = _pedir(_token())

    assert response.status_code == 500
    assert "VITE_CLERK_PUBLISHABLE_KEY" in response.json()["detail"]
    clerk_real.assert_not_called()
