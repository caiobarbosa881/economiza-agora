"""Testes do fluxo de redefinição de senha."""

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User

REQUEST_URL = reverse("accounts:password-reset")
CONFIRM_URL = reverse("accounts:password-reset-confirm")


@pytest.mark.django_db
def test_solicitacao_envia_email(api_client: APIClient, user: User, mailoutbox) -> None:
    """Solicitação com e-mail existente dispara o e-mail de reset."""
    response = api_client.post(REQUEST_URL, {"email": user.email})

    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 1


@pytest.mark.django_db
def test_solicitacao_email_inexistente(api_client: APIClient, mailoutbox) -> None:
    """Solicitação com e-mail inexistente não revela a ausência e não envia e-mail."""
    response = api_client.post(REQUEST_URL, {"email": "naoexiste@example.com"})

    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 0


@pytest.mark.django_db
def test_confirmacao_redefine_senha(api_client: APIClient, user: User) -> None:
    """Token válido define a nova senha."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = api_client.post(
        CONFIRM_URL,
        {
            "uid": uid,
            "token": token,
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "NovaSenhaForte123",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("NovaSenhaForte123")


@pytest.mark.django_db
def test_confirmacao_token_invalido(api_client: APIClient, user: User) -> None:
    """Token inválido é rejeitado."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    response = api_client.post(
        CONFIRM_URL,
        {
            "uid": uid,
            "token": "token-invalido",
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "NovaSenhaForte123",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
