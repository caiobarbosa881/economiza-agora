"""Testes do endpoint de health check do app ``core``."""

import pytest
from django.db import DatabaseError
from rest_framework import status
from rest_framework.test import APIClient

HEALTH_URL = "/api/health/"


@pytest.mark.django_db
def test_health_check_retorna_ok(api_client: APIClient) -> None:
    """Com o banco respondendo, o health check devolve 200."""
    response = api_client.get(HEALTH_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.django_db
def test_health_check_banco_indisponivel_retorna_503(
    api_client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Se a consulta ao banco falhar, o health check devolve 503."""

    def cursor_quebrado(*args, **kwargs):
        raise DatabaseError("conexão recusada")

    monkeypatch.setattr("apps.core.views.connection.cursor", cursor_quebrado)

    response = api_client.get(HEALTH_URL)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"status": "error", "database": "unavailable"}
