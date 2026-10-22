"""Serializers do perfil financeiro."""

from rest_framework import serializers

from apps.finances.models import EXPENSE_FIELDS, FinancialProfile


class FinancialProfileSerializer(serializers.ModelSerializer):
    """Leitura e atualização do perfil financeiro com totais calculados."""

    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = FinancialProfile
        fields = ("monthly_income", *EXPENSE_FIELDS, "total_expenses", "balance", "updated_at")
        read_only_fields = ("updated_at",)
