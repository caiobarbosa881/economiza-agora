"""Testes do endpoint de health check do app ``core``."""

from rest_framework import status
from rest_framework.test import APIClient


def test_health_check_retorna_ok(api_client: APIClient) -> None:
    """O endpoint de health deve responder 200 com status ``ok``."""
    response = api_client.get("/api/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
