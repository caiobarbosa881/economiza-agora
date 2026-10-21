"""Testes da política de CORS da API."""

import pytest
from rest_framework.test import APIClient

ORIGEM_FRONTEND = "https://app.example.com"


@pytest.fixture(autouse=True)
def _cors_restrito(settings) -> None:
    """Libera apenas a origem do frontend de teste."""
    settings.CORS_ALLOWED_ORIGINS = [ORIGEM_FRONTEND]


def test_preflight_origem_permitida_recebe_cabecalhos_cors(api_client: APIClient) -> None:
    """Preflight vindo do frontend recebe ``Access-Control-Allow-Origin``."""
    response = api_client.options(
        "/api/auth/login/",
        HTTP_ORIGIN=ORIGEM_FRONTEND,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
    )

    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == ORIGEM_FRONTEND


@pytest.mark.django_db
def test_origem_nao_permitida_nao_recebe_cabecalho_cors(api_client: APIClient) -> None:
    """Origem fora da lista não recebe o cabeçalho e o navegador bloqueia."""
    response = api_client.get("/api/health/", HTTP_ORIGIN="https://malicioso.example.com")

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response
