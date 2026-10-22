"""Testes do modelo de perfil financeiro."""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.finances.models import FinancialProfile


@pytest.mark.django_db
def test_perfil_novo_comeca_zerado(user: User) -> None:
    """Um perfil recém-criado tem renda, gastos e saldo zerados."""
    profile = FinancialProfile.objects.create(user=user)

    assert profile.monthly_income == Decimal("0")
    assert profile.total_expenses == Decimal("0")
    assert profile.balance == Decimal("0")


@pytest.mark.django_db
def test_total_e_saldo(user: User) -> None:
    """Total soma todos os gastos e saldo é a renda menos esse total."""
    profile = FinancialProfile.objects.create(
        user=user,
        monthly_income=Decimal("5000"),
        housing=Decimal("1500"),
        food=Decimal("800.50"),
        phone=Decimal("59.90"),
        subscriptions=Decimal("45.90"),
    )

    assert profile.total_expenses == Decimal("2406.30")
    assert profile.balance == Decimal("2593.70")


@pytest.mark.django_db
def test_saldo_negativo_indica_deficit(user: User) -> None:
    """Gastos maiores que a renda resultam em saldo negativo."""
    profile = FinancialProfile.objects.create(
        user=user, monthly_income=Decimal("1000"), housing=Decimal("1200")
    )

    assert profile.balance == Decimal("-200")


@pytest.mark.django_db
def test_valor_negativo_invalido(user: User) -> None:
    """Valores monetários negativos não passam na validação do modelo."""
    profile = FinancialProfile(user=user, food=Decimal("-1"))

    with pytest.raises(ValidationError):
        profile.full_clean()


@pytest.mark.django_db
def test_str(user: User) -> None:
    """A representação textual identifica o usuário."""
    profile = FinancialProfile.objects.create(user=user)

    assert str(profile) == f"Perfil financeiro de {user.email}"
