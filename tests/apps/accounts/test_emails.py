"""Testes dos e-mails transacionais."""

import pytest
from django.conf import settings

from apps.accounts.emails import send_password_reset_email, send_verification_email
from apps.accounts.models import User

PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_send_verification_email_conteudo(user: User, mailoutbox) -> None:
    """O e-mail de verificação vai para o usuário com o link correto."""
    send_verification_email(user)

    email = mailoutbox[0]
    assert email.to == [user.email]
    assert "Confirme seu e-mail" in email.subject
    assert f"{settings.FRONTEND_URL}/verify-email?uid=" in email.body
    assert "token=" in email.body
    assert user.first_name in email.body


@pytest.mark.django_db
def test_send_verification_email_sem_nome_usa_email(db, mailoutbox) -> None:
    """Sem first_name, a saudação usa o próprio e-mail."""
    user = User.objects.create_user(email="anonimo@example.com", password=PASSWORD)

    send_verification_email(user)

    assert "anonimo@example.com" in mailoutbox[0].body


@pytest.mark.django_db
def test_send_password_reset_email_conteudo(user: User, mailoutbox) -> None:
    """O e-mail de redefinição vai para o usuário com o link correto."""
    send_password_reset_email(user)

    email = mailoutbox[0]
    assert email.to == [user.email]
    assert "Redefinição de senha" in email.subject
    assert f"{settings.FRONTEND_URL}/reset-password?uid=" in email.body
    assert "token=" in email.body
