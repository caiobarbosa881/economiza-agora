"""Testes do endpoint de registro."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User

REGISTER_URL = reverse("accounts:register")
PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_registro_cria_usuario_e_envia_email(api_client: APIClient, mailoutbox) -> None:
    """Registro válido cria o usuário e dispara o e-mail de verificação."""
    payload = {
        "email": "novo@example.com",
        "first_name": "Novo",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }

    response = api_client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "novo@example.com"
    user = User.objects.get(email="novo@example.com")
    assert user.is_email_verified is False
    assert user.check_password(PASSWORD)
    assert len(mailoutbox) == 1


@pytest.mark.django_db
def test_registro_email_duplicado(api_client: APIClient, user: User) -> None:
    """Não permite cadastrar e-mail já existente."""
    payload = {
        "email": user.email,
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }

    response = api_client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.json()


@pytest.mark.django_db
def test_registro_senhas_diferentes(api_client: APIClient) -> None:
    """Recusa quando a confirmação de senha não coincide."""
    payload = {
        "email": "novo@example.com",
        "password": PASSWORD,
        "password_confirm": "OutraSenha123",
    }

    response = api_client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_registro_senha_fraca(api_client: APIClient) -> None:
    """Recusa senhas que não passam nos validadores do Django."""
    payload = {
        "email": "novo@example.com",
        "password": "123",
        "password_confirm": "123",
    }

    response = api_client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
