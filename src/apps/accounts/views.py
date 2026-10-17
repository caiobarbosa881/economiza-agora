"""Views de autenticação e conta."""

import logging

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.emails import send_password_reset_email, send_verification_email
from apps.accounts.models import User
from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    EmailVerificationSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from apps.accounts.throttles import (
    LoginRateThrottle,
    PasswordResetRateThrottle,
    RegisterRateThrottle,
)

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """Cria uma nova conta e envia o e-mail de verificação."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]


class LoginView(TokenObtainPairView):
    """Autentica o usuário e devolve access, refresh e seus dados."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]


class RefreshView(TokenRefreshView):
    """Renova o access token e devolve os dados do usuário."""

    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """Invalida o refresh token informado (blacklist)."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Adiciona o refresh token à blacklist."""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response(
                {"detail": "Token inválido ou já expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Logout realizado com sucesso."},
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """Consulta e atualiza os dados do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        """Retorna o próprio usuário autenticado."""
        return self.request.user

    def get_serializer_class(self) -> type:
        """Usa o serializer de atualização em requisições de escrita."""
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer


class PasswordChangeView(APIView):
    """Troca a senha do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Valida e persiste a nova senha."""
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha alterada com sucesso."})


class PasswordResetRequestView(APIView):
    """Solicita o envio do link de redefinição de senha."""

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request: Request) -> Response:
        """Envia o e-mail se o usuário existir, sem revelar isso na resposta."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"]
        ).first()
        if user is not None:
            try:
                send_password_reset_email(user)
            except Exception:  # noqa: BLE001 - não expor falha de envio ao cliente
                logger.exception("Falha ao enviar e-mail de redefinição de senha.")
        return Response(
            {"detail": "Se o e-mail existir, enviaremos as instruções."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """Conclui a redefinição de senha com uid e token."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Valida o token e define a nova senha."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha redefinida com sucesso."})


class EmailVerificationView(APIView):
    """Confirma o e-mail a partir de uid e token."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Marca o e-mail como verificado."""
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "E-mail verificado com sucesso."})


class EmailResendView(APIView):
    """Reenvia o e-mail de verificação para o usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Reenvia o e-mail se ainda não estiver verificado."""
        if request.user.is_email_verified:
            return Response({"detail": "O e-mail já está verificado."})
        send_verification_email(request.user)
        return Response({"detail": "E-mail de verificação reenviado."})
