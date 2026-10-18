"""Testes dos throttles dos endpoints de autenticação."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.throttles import LoginRateThrottle

LOGIN_URL = reverse("accounts:login")
PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_login_bloqueia_apos_exceder_rate(
    api_client: APIClient, user: User, monkeypatch
) -> None:
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
