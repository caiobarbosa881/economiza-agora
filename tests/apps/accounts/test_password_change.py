"""Testes de troca de senha."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User

CHANGE_URL = reverse("accounts:password-change")
PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_troca_senha_com_sucesso(auth_client: APIClient, user: User) -> None:
    """Troca de senha válida persiste a nova senha."""
    response = auth_client.post(
        CHANGE_URL,
        {
            "current_password": PASSWORD,
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "NovaSenhaForte123",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("NovaSenhaForte123")


@pytest.mark.django_db
def test_troca_senha_atual_incorreta(auth_client: APIClient) -> None:
    """Recusa quando a senha atual está errada."""
    response = auth_client.post(
        CHANGE_URL,
        {
            "current_password": "errada",
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "NovaSenhaForte123",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_troca_senha_exige_autenticacao(api_client: APIClient) -> None:
    """Troca de senha exige usuário autenticado."""
    response = api_client.post(
        CHANGE_URL,
        {
            "current_password": PASSWORD,
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "NovaSenhaForte123",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_troca_senha_confirmacao_divergente(auth_client: APIClient) -> None:
    """Nova senha e confirmação diferentes são rejeitadas."""
    response = auth_client.post(
        CHANGE_URL,
        {
            "current_password": PASSWORD,
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "OutraSenha123",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "new_password_confirm" in response.json()
