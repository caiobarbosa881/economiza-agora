"""Testes de verificação de e-mail."""

import pytest
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.tokens import email_verification_token

VERIFY_URL = reverse("accounts:email-verify")
RESEND_URL = reverse("accounts:email-resend")


@pytest.mark.django_db
def test_verificacao_com_token_valido(api_client: APIClient, user: User) -> None:
    """Token válido marca o e-mail como verificado."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    response = api_client.post(VERIFY_URL, {"uid": uid, "token": token})

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.is_email_verified is True


@pytest.mark.django_db
def test_verificacao_token_invalido(api_client: APIClient, user: User) -> None:
    """Token inválido é rejeitado."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    response = api_client.post(VERIFY_URL, {"uid": uid, "token": "invalido"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_verificacao_uid_invalido(api_client: APIClient) -> None:
    """UID que não decodifica é rejeitado no campo ``uid``."""
    response = api_client.post(VERIFY_URL, {"uid": "nao-e-um-uid", "token": "x"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "uid" in response.json()


@pytest.mark.django_db
def test_verificacao_quando_ja_verificado(verified_client: APIClient, verified_user: User) -> None:
    """E-mail já verificado é rejeitado antes da checagem do token."""
    uid = urlsafe_base64_encode(force_bytes(verified_user.pk))

    response = verified_client.post(VERIFY_URL, {"uid": uid, "token": "qualquer"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Este e-mail já foi verificado." in response.json()["detail"]


@pytest.mark.django_db
def test_reenvio_envia_email(auth_client: APIClient, user: User, mailoutbox) -> None:
    """Reenvio para usuário não verificado dispara o e-mail."""
    response = auth_client.post(RESEND_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 1


@pytest.mark.django_db
def test_reenvio_quando_ja_verificado(verified_client: APIClient, mailoutbox) -> None:
    """Reenvio para e-mail já verificado não dispara novo e-mail."""
    response = verified_client.post(RESEND_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 0
