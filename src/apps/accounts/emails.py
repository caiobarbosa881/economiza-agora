"""Envio de e-mails transacionais da aplicação."""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.models import User
from apps.accounts.tokens import email_verification_token


def send_verification_email(user: User) -> None:
    """Envia o e-mail com o link de verificação de conta.

    Args:
        user: Usuário que receberá o e-mail.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    link = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}"
    send_mail(
        subject="Confirme seu e-mail - Economiza Agora",
        message=(
            f"Olá, {user.first_name or user.email}!\n\n"
            f"Confirme seu e-mail acessando o link abaixo:\n{link}\n\n"
            "Se você não solicitou este cadastro, ignore esta mensagem."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_password_reset_email(user: User) -> None:
    """Envia o e-mail com o link de redefinição de senha.

    Args:
        user: Usuário que receberá o e-mail.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
    send_mail(
        subject="Redefinição de senha - Economiza Agora",
        message=(
            f"Olá, {user.first_name or user.email}!\n\n"
            f"Para redefinir sua senha, acesse o link abaixo:\n{link}\n\n"
            "Se você não solicitou a redefinição, ignore esta mensagem."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
