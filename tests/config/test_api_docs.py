"""Testes do schema OpenAPI e da documentação da API."""

from rest_framework.test import APIClient


def test_schema_openapi_lista_endpoints_de_autenticacao(api_client: APIClient) -> None:
    """O schema é público em desenvolvimento e documenta as rotas de auth."""
    response = api_client.get("/api/schema/", HTTP_ACCEPT="application/vnd.oai.openapi+json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.")
    assert "/api/auth/login/" in schema["paths"]
    assert "/api/auth/logout/" in schema["paths"]
    assert "/api/health/" in schema["paths"]


def test_swagger_ui_disponivel(api_client: APIClient) -> None:
    """A página de documentação interativa responde com HTML."""
    response = api_client.get("/api/docs/")

    assert response.status_code == 200
    assert "swagger" in response.content.decode().lower()
