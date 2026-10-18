"""Jornada crítica de ponta a ponta: cadastro → login → perfil → logout.

Diferente dos testes de feature, aqui o cliente usa o fluxo real de JWT
(obtidos pelo login) em vez de ``force_authenticate``.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

REGISTER_URL = reverse("accounts:register")
LOGIN_URL = reverse("accounts:login")
ME_URL = reverse("accounts:me")
LOGOUT_URL = reverse("accounts:logout")
PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_jornada_cadastro_login_perfil_logout(api_client: APIClient, mailoutbox) -> None:
    """Usuário novo percorre o fluxo completo de conta com tokens reais."""
    registro = api_client.post(
        REGISTER_URL,
        {
            "email": "jornada@example.com",
            "first_name": "Jornada",
            "password": PASSWORD,
            "password_confirm": PASSWORD,
        },
    )
    assert registro.status_code == status.HTTP_201_CREATED
    assert len(mailoutbox) == 1

    login = api_client.post(
        LOGIN_URL, {"email": "jornada@example.com", "password": PASSWORD}
    )
    assert login.status_code == status.HTTP_200_OK
    tokens = login.json()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    me = api_client.get(ME_URL)
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["email"] == "jornada@example.com"
    assert me.json()["is_email_verified"] is False

    logout = api_client.post(LOGOUT_URL, {"refresh": tokens["refresh"]})
    assert logout.status_code == status.HTTP_200_OK

    api_client.credentials()
    refresh_apos_logout = api_client.post(
        reverse("accounts:refresh"), {"refresh": tokens["refresh"]}
    )
    assert refresh_apos_logout.status_code == status.HTTP_401_UNAUTHORIZED
