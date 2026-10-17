"""Fixtures compartilhadas entre os testes."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Retorna um cliente de API do Django REST Framework.

    Returns:
        Instância de ``APIClient`` pronta para uso.
    """
    return APIClient()
