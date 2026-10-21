"""Throttles específicos dos endpoints de autenticação."""

from rest_framework.request import Request
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle, UserRateThrottle
from rest_framework.views import APIView


class LoginRateThrottle(AnonRateThrottle):
    """Limita tentativas de login por IP."""

    scope = "login"


class RegisterRateThrottle(AnonRateThrottle):
    """Limita criações de conta por IP."""

    scope = "register"


class PasswordResetRateThrottle(AnonRateThrottle):
    """Limita solicitações de redefinição de senha por IP."""

    scope = "password_reset"


class EmailResendRateThrottle(UserRateThrottle):
    """Limita reenvios do e-mail de verificação por usuário."""

    scope = "email_resend"


class TokenConfirmRateThrottle(SimpleRateThrottle):
    """Limita confirmações com token (verificação de e-mail e reset de senha).

    Diferente de ``AnonRateThrottle``, conta por IP mesmo quando a requisição
    está autenticada, para que estar logado não sirva de atalho para tentar
    tokens em sequência.
    """

    scope = "token_confirm"

    def get_cache_key(self, request: Request, view: APIView) -> str:
        """Usa o IP do cliente como identificador do limite.

        Args:
            request: Requisição HTTP recebida.
            view: View que está sendo acessada.

        Returns:
            Chave de cache do limite para este IP.
        """
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}
