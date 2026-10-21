"""Testes dos throttles dos endpoints de autenticação."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.throttles import (
    EmailResendRateThrottle,
    LoginRateThrottle,
    TokenConfirmRateThrottle,
)

LOGIN_URL = reverse("accounts:login")
EMAIL_RESEND_URL = reverse("accounts:email-resend")
EMAIL_VERIFY_URL = reverse("accounts:email-verify")
PASSWORD_RESET_CONFIRM_URL = reverse("accounts:password-reset-confirm")
TOKEN_INVALIDO = {"uid": "invalido", "token": "invalido"}
PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_login_bloqueia_apos_exceder_rate(api_client: APIClient, user: User, monkeypatch) -> None:
    """Após exceder a rate de login, o IP recebe 429.

    O DRF amarra ``THROTTLE_RATES`` na importação do módulo de throttling,
    então a rate é sobrescrita na classe em vez de via ``settings``.
    """
    monkeypatch.setattr(LoginRateThrottle, "THROTTLE_RATES", {"login": "2/min"})
    payload = {"email": user.email, "password": "senha-errada"}

    primeira = api_client.post(LOGIN_URL, payload)
    segunda = api_client.post(LOGIN_URL, payload)
    terceira = api_client.post(LOGIN_URL, payload)

    assert primeira.status_code == status.HTTP_401_UNAUTHORIZED
    assert segunda.status_code == status.HTTP_401_UNAUTHORIZED
    assert terceira.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_reenvio_de_email_bloqueia_apos_exceder_rate(auth_client: APIClient, monkeypatch) -> None:
    """O reenvio do e-mail de verificação é limitado por usuário."""
    monkeypatch.setattr(EmailResendRateThrottle, "THROTTLE_RATES", {"email_resend": "2/min"})

    respostas = [auth_client.post(EMAIL_RESEND_URL) for _ in range(3)]

    assert [r.status_code for r in respostas] == [
        status.HTTP_200_OK,
        status.HTTP_200_OK,
        status.HTTP_429_TOO_MANY_REQUESTS,
    ]


@pytest.mark.django_db
@pytest.mark.parametrize("url", [EMAIL_VERIFY_URL, PASSWORD_RESET_CONFIRM_URL])
def test_confirmacao_de_token_bloqueia_apos_exceder_rate(
    api_client: APIClient, monkeypatch, url: str
) -> None:
    """Tentativas de token em sequência no mesmo IP recebem 429."""
    monkeypatch.setattr(TokenConfirmRateThrottle, "THROTTLE_RATES", {"token_confirm": "2/min"})
    payload = {**TOKEN_INVALIDO, "new_password": PASSWORD, "new_password_confirm": PASSWORD}

    respostas = [api_client.post(url, payload) for _ in range(3)]

    assert [r.status_code for r in respostas] == [
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_429_TOO_MANY_REQUESTS,
    ]


@pytest.mark.django_db
def test_confirmacao_de_token_limita_mesmo_autenticado(auth_client: APIClient, monkeypatch) -> None:
    """Estar autenticado não contorna o limite por IP das confirmações."""
    monkeypatch.setattr(TokenConfirmRateThrottle, "THROTTLE_RATES", {"token_confirm": "1/min"})

    primeira = auth_client.post(EMAIL_VERIFY_URL, TOKEN_INVALIDO)
    segunda = auth_client.post(EMAIL_VERIFY_URL, TOKEN_INVALIDO)

    assert primeira.status_code == status.HTTP_400_BAD_REQUEST
    assert segunda.status_code == status.HTTP_429_TOO_MANY_REQUESTS
