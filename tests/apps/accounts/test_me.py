"""Testes do endpoint de perfil (me)."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User

ME_URL = reverse("accounts:me")


@pytest.mark.django_db
def test_me_autenticado(auth_client: APIClient, user: User) -> None:
    """Usuário autenticado consulta os próprios dados."""
    response = auth_client.get(ME_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == user.email


@pytest.mark.django_db
def test_me_anonimo(api_client: APIClient) -> None:
    """Acesso anônimo é rejeitado."""
    response = api_client.get(ME_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_atualiza_dados(auth_client: APIClient, user: User) -> None:
    """Usuário autenticado atualiza nome e sobrenome."""
    response = auth_client.patch(ME_URL, {"first_name": "Atualizado"})

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.first_name == "Atualizado"
