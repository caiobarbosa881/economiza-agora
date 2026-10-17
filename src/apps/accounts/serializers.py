"""Serializers de autenticação e conta."""

from typing import Any, cast

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.emails import send_verification_email
from apps.accounts.models import User
from apps.accounts.tokens import email_verification_token

PASSWORD_STYLE = {"write_only": True, "style": {"input_type": "password"}}


def _decode_uid(uid: str) -> User:
    """Decodifica o UID em base64 e retorna o usuário correspondente.

    Args:
        uid: Identificador codificado em base64.

    Returns:
        A instância de usuário encontrada.

    Raises:
        serializers.ValidationError: Se o UID for inválido.
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        return User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
        raise serializers.ValidationError(
            {"uid": "Identificador inválido."}
        ) from exc


class UserSerializer(serializers.ModelSerializer):
    """Representação pública de um usuário."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_email_verified",
            "date_joined",
        )
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """Atualização dos dados básicos do usuário autenticado."""

    class Meta:
        model = User
        fields = ("first_name", "last_name")


class RegisterSerializer(serializers.ModelSerializer):
    """Criação de conta com confirmação de senha."""

    password = serializers.CharField(**PASSWORD_STYLE)
    password_confirm = serializers.CharField(**PASSWORD_STYLE)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "password", "password_confirm")
        read_only_fields = ("id",)

    def validate_email(self, value: str) -> str:
        """Garante que o e-mail ainda não esteja em uso."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Já existe um usuário com este e-mail.")
        return value.lower()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida a confirmação e a força da senha."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Cria o usuário e dispara o e-mail de verificação."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        send_verification_email(user)
        return user

    def to_representation(self, instance: User) -> dict[str, Any]:
        """Retorna os dados públicos do usuário criado."""
        return UserSerializer(instance).data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login que devolve os tokens e os dados do usuário."""

    @classmethod
    def get_token(cls, user: User) -> RefreshToken:
        """Adiciona claims customizadas ao token."""
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Inclui os dados do usuário na resposta de login."""
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """Refresh que devolve os dados do usuário junto ao novo access."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Resolve o usuário antes da rotação e anexa à resposta.

        O usuário é resolvido a partir do refresh recebido antes de
        ``super().validate``, pois a rotação invalida (blacklist) o token
        original.
        """
        refresh = RefreshToken(attrs["refresh"])
        user = User.objects.get(pk=refresh.payload.get("user_id"))
        data = super().validate(attrs)
        data["user"] = UserSerializer(user).data
        return data


class LogoutSerializer(serializers.Serializer):
    """Recebe o refresh token a ser invalidado."""

    refresh = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    """Troca de senha do usuário autenticado."""

    current_password = serializers.CharField(**PASSWORD_STYLE)
    new_password = serializers.CharField(**PASSWORD_STYLE)
    new_password_confirm = serializers.CharField(**PASSWORD_STYLE)

    def validate_current_password(self, value: str) -> str:
        """Confere se a senha atual está correta."""
        user = cast(User, self.context["request"].user)
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida a confirmação e a força da nova senha."""
        user = cast(User, self.context["request"].user)
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "As senhas não coincidem."}
            )
        validate_password(attrs["new_password"], user)
        return attrs

    def save(self, **kwargs: Any) -> User:
        """Persiste a nova senha com hash."""
        user = cast(User, self.context["request"].user)
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Solicitação de redefinição de senha por e-mail."""

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        """Normaliza o e-mail informado."""
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Conclusão da redefinição de senha com uid e token."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(**PASSWORD_STYLE)
    new_password_confirm = serializers.CharField(**PASSWORD_STYLE)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida o token e as novas senhas."""
        user = _decode_uid(attrs["uid"])
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "Token inválido ou expirado."}
            )
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "As senhas não coincidem."}
            )
        validate_password(attrs["new_password"], user)
        self.user = user
        return attrs

    def save(self, **kwargs: Any) -> User:
        """Define a nova senha do usuário."""
        user = cast(User, self.user)
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Confirmação de e-mail com uid e token."""

    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida o token de verificação de e-mail."""
        user = _decode_uid(attrs["uid"])
        if user.is_email_verified:
            raise serializers.ValidationError(
                {"detail": "Este e-mail já foi verificado."}
            )
        if not email_verification_token.check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "Token inválido ou expirado."}
            )
        self.user = user
        return attrs

    def save(self, **kwargs: Any) -> User:
        """Marca o e-mail do usuário como verificado."""
        user = cast(User, self.user)
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified", "updated_at"])
        return user
