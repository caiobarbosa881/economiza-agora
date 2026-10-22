"""Modelo de perfil financeiro do usuário."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

# Campos de gasto mensal, na ordem em que aparecem na API e no admin.
EXPENSE_FIELDS = (
    "housing",
    "utilities",
    "food",
    "transport",
    "phone",
    "internet",
    "subscriptions",
    "other",
)


def _money_field(verbose_name: str) -> models.DecimalField:
    """Cria um campo monetário não negativo com valor padrão zero.

    Args:
        verbose_name: Nome legível do campo.

    Returns:
        Um ``DecimalField`` configurado para valores em reais.
    """
    return models.DecimalField(
        verbose_name,
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )


class FinancialProfile(models.Model):
    """Renda e gastos fixos mensais informados pelo usuário."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="financial_profile",
        verbose_name="usuário",
    )
    monthly_income = _money_field("renda mensal")
    housing = _money_field("moradia")
    utilities = _money_field("contas da casa")
    food = _money_field("alimentação")
    transport = _money_field("transporte")
    phone = _money_field("plano de celular")
    internet = _money_field("internet")
    subscriptions = _money_field("assinaturas")
    other = _money_field("outros")
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "perfil financeiro"
        verbose_name_plural = "perfis financeiros"

    def __str__(self) -> str:
        """Retorna o e-mail do usuário dono do perfil."""
        return f"Perfil financeiro de {self.user}"

    @property
    def total_expenses(self) -> Decimal:
        """Retorna a soma dos gastos mensais."""
        return sum((getattr(self, field) for field in EXPENSE_FIELDS), Decimal("0"))

    @property
    def balance(self) -> Decimal:
        """Retorna a renda menos os gastos (negativo indica déficit)."""
        return self.monthly_income - self.total_expenses
