"""Throttles específicos dos endpoints de autenticação."""

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Limita tentativas de login por IP."""

    scope = "login"


class RegisterRateThrottle(AnonRateThrottle):
    """Limita criações de conta por IP."""

    scope = "register"


class PasswordResetRateThrottle(AnonRateThrottle):
    """Limita solicitações de redefinição de senha por IP."""

    scope = "password_reset"
