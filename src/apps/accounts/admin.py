"""Registro do usuário customizado no Django Admin."""

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin do modelo :class:`apps.accounts.models.User`."""

    ordering = ("-date_joined",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_email_verified",
        "is_staff",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "is_email_verified")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("date_joined", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados pessoais", {"fields": ("first_name", "last_name")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_email_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas", {"fields": ("last_login", "date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    def get_readonly_fields(self, request: HttpRequest, obj: Any = None) -> tuple[str, ...]:
        """Impede a alteração das datas após a criação."""
        if obj is not None:
            return self.readonly_fields
        return ("updated_at",)
