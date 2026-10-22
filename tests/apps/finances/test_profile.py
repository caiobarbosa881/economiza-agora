"""Testes do endpoint de perfil financeiro."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.finances.models import FinancialProfile

PROFILE_URL = reverse("finances:profile")


@pytest.mark.django_db
def test_anonimo_rejeitado(api_client: APIClient) -> None:
    """Acesso anônimo é rejeitado."""
    response = api_client.get(PROFILE_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_primeiro_acesso_cria_perfil_zerado(auth_client: APIClient, user: User) -> None:
    """O primeiro GET cria o perfil com todos os valores zerados."""
    response = auth_client.get(PROFILE_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["monthly_income"] == "0.00"
    assert data["total_expenses"] == "0.00"
    assert data["balance"] == "0.00"
    assert FinancialProfile.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_get_repetido_nao_duplica_perfil(auth_client: APIClient, user: User) -> None:
    """Acessos seguintes reutilizam o mesmo perfil."""
    auth_client.get(PROFILE_URL)
    auth_client.get(PROFILE_URL)

    assert FinancialProfile.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_patch_atualiza_e_recalcula(auth_client: APIClient, user: User) -> None:
    """PATCH parcial grava os valores e devolve total e saldo atualizados."""
    response = auth_client.patch(
        PROFILE_URL,
        {"monthly_income": "4000.00", "housing": "1200.00", "internet": "99.90"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_expenses"] == "1299.90"
    assert data["balance"] == "2700.10"
    profile = FinancialProfile.objects.get(user=user)
    assert str(profile.internet) == "99.90"


@pytest.mark.django_db
def test_patch_valor_negativo(auth_client: APIClient) -> None:
    """Valores negativos são rejeitados com 400."""
    response = auth_client.patch(PROFILE_URL, {"food": "-10"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "food" in response.json()


@pytest.mark.django_db
def test_campos_calculados_sao_somente_leitura(auth_client: APIClient) -> None:
    """Total e saldo enviados pelo cliente são ignorados."""
    response = auth_client.patch(
        PROFILE_URL,
        {"monthly_income": "100", "balance": "999999", "total_expenses": "1"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["balance"] == "100.00"


@pytest.mark.django_db
def test_usuario_ve_apenas_o_proprio_perfil(
    api_client: APIClient, user: User, verified_user: User
) -> None:
    """Cada usuário acessa somente o seu perfil."""
    FinancialProfile.objects.create(user=verified_user, monthly_income="9000")
    api_client.force_authenticate(user=user)

    response = api_client.get(PROFILE_URL)

    assert response.json()["monthly_income"] == "0.00"
    assert FinancialProfile.objects.get(user=verified_user).monthly_income == 9000
