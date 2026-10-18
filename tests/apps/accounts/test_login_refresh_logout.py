"""Testes de login, refresh e logout."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User

LOGIN_URL = reverse("accounts:login")
REFRESH_URL = reverse("accounts:refresh")
LOGOUT_URL = reverse("accounts:logout")
PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_login_retorna_tokens_e_usuario(api_client: APIClient, user: User) -> None:
    """Login válido devolve access, refresh e os dados do usuário."""
    response = api_client.post(
        LOGIN_URL, {"email": user.email, "password": PASSWORD}
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access" in body
    assert "refresh" in body
    assert body["user"]["email"] == user.email


@pytest.mark.django_db
def test_login_senha_incorreta(api_client: APIClient, user: User) -> None:
    """Login com senha errada é rejeitado."""
    response = api_client.post(
        LOGIN_URL, {"email": user.email, "password": "senha-errada"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_refresh_devolve_novo_access(api_client: APIClient, user: User) -> None:
    """Refresh válido devolve novo access e os dados do usuário."""
    login = api_client.post(LOGIN_URL, {"email": user.email, "password": PASSWORD})
    refresh = login.json()["refresh"]

    response = api_client.post(REFRESH_URL, {"refresh": refresh})

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access" in body
    assert body["user"]["email"] == user.email


@pytest.mark.django_db
def test_logout_invalida_refresh(api_client: APIClient, user: User) -> None:
    """Após o logout o refresh token não pode mais ser usado."""
    login = api_client.post(LOGIN_URL, {"email": user.email, "password": PASSWORD})
    refresh = login.json()["refresh"]
    api_client.force_authenticate(user=user)

    logout = api_client.post(LOGOUT_URL, {"refresh": refresh})
    assert logout.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=None)
    reused = api_client.post(REFRESH_URL, {"refresh": refresh})
    assert reused.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_exige_autenticacao(api_client: APIClient) -> None:
    """Logout sem autenticação é rejeitado."""
    response = api_client.post(LOGOUT_URL, {"refresh": "token"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_refresh_invalido(auth_client: APIClient) -> None:
    """Refresh token malformado/inválido devolve 400 com detail."""
    response = auth_client.post(LOGOUT_URL, {"refresh": "token-invalido"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Token inválido ou já expirado."


@pytest.mark.django_db
def test_logout_sem_campo_refresh(auth_client: APIClient) -> None:
    """Logout sem o campo ``refresh`` falha na validação do serializer."""
    response = auth_client.post(LOGOUT_URL, {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "refresh" in response.json()
