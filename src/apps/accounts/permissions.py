"""Permissões customizadas do app ``accounts``."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import User


class IsEmailVerified(BasePermission):
    """Permite acesso apenas a usuários com e-mail verificado."""

    message = "É necessário verificar o e-mail para acessar este recurso."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Verifica autenticação e o campo ``is_email_verified``."""
        user = request.user
        return bool(
            isinstance(user, User)
            and user.is_authenticated
            and user.is_email_verified
        )
