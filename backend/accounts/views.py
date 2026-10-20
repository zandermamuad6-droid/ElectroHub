
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token

from rest_framework import permissions, status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def csrf_token(request):
    token = get_token(request)
    response = Response({"csrfToken": token})
    return response


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    return Response(
        {
            "message": "Account created successfully.",
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return Response(
            {"detail": "Invalid username or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    login(request, user)

    return Response(
        {
            "message": "Login successful.",
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def logout_view(request):
    logout(request)

    return Response(
        {"message": "Logout successful."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def current_user(request):
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return Response(
        UserSerializer(request.user).data,
        status=status.HTTP_200_OK,
    )
