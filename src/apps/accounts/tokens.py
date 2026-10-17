"""Geradores de tokens assinados usados nos fluxos de conta."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from apps.accounts.models import User


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Gera tokens de verificação de e-mail.

    O token deixa de ser válido assim que ``is_email_verified`` muda, o que
    impede reutilização após a confirmação.
    """

    def _make_hash_value(self, user: User, timestamp: int) -> str:
        """Monta o valor base do hash do token.

        Args:
            user: Usuário alvo da verificação.
            timestamp: Instante de emissão do token.

        Returns:
            String usada para compor o token assinado.
        """
        return f"{user.pk}{user.is_email_verified}{user.email}{timestamp}"


email_verification_token = EmailVerificationTokenGenerator()
