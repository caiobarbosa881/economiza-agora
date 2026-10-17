"""Fixtures compartilhadas entre os testes."""

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture(autouse=True)
def _reset_state(settings) -> None:
    """Limpa o cache de throttling e usa o backend de e-mail em memória."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client() -> APIClient:
    """Retorna um cliente de API do Django REST Framework.

    Returns:
        Instância de ``APIClient`` pronta para uso.
    """
    return APIClient()


@pytest.fixture
def user(db) -> User:
    """Cria um usuário comum para os testes."""
    return User.objects.create_user(
        email="user@example.com",
        password="SenhaForte123",
        first_name="Fulano",
    )


@pytest.fixture
def verified_user(db) -> User:
    """Cria um usuário com e-mail já verificado."""
    return User.objects.create_user(
        email="verified@example.com",
        password="SenhaForte123",
        is_email_verified=True,
    )


@pytest.fixture
def auth_client(api_client: APIClient, user: User) -> APIClient:
    """Cliente autenticado como ``user``."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def verified_client(api_client: APIClient, verified_user: User) -> APIClient:
    """Cliente autenticado como ``verified_user``."""
    api_client.force_authenticate(user=verified_user)
    return api_client
