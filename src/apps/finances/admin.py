"""Registro do perfil financeiro no Django Admin."""

from django.contrib import admin

from apps.finances.models import EXPENSE_FIELDS, FinancialProfile


@admin.register(FinancialProfile)
class FinancialProfileAdmin(admin.ModelAdmin):
    """Admin do modelo :class:`apps.finances.models.FinancialProfile`."""

    list_display = ("user", "monthly_income", "total_expenses", "balance", "updated_at")
    search_fields = ("user__email",)
    raw_id_fields = ("user",)
    readonly_fields = ("total_expenses", "balance", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "monthly_income")}),
        ("Gastos mensais", {"fields": EXPENSE_FIELDS}),
        ("Resumo", {"fields": ("total_expenses", "balance")}),
        ("Datas", {"fields": ("created_at", "updated_at")}),
    )
