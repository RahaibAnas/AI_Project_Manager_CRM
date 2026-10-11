from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, TeamSerializer,CustomUserSerializer
from .permissions import IsAdmin

User = get_user_model()

# Create your views here.


@api_view(["POST"])
@permission_classes([IsAdmin])
def register(request):
    print(request.path)
    is_many = isinstance(request.data, list)
    serializer = UserSerializer(data=request.data, many=is_many)
    if not serializer.is_valid():
        return Response(
            {"success": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save()
    return Response(
        {
            "success": True,
            "message": "User Registered successfully",
        }
    )


@api_view(["POST"])
def login(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")
    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response(
            {"success": False, "error": "invalid Credentials"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user.token_verified = True
    user.save(update_fields=["token_verified"])
    refresh = RefreshToken.for_user(user)
    refresh["token_verified"] = user.token_verified
    return Response(
        {
            "success": True,
            "message": "User login Successfully",
            "access token": str(refresh.access_token),
            "refresh token": str(refresh),
        },
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(request.user)

    return Response(
        {
            "success": True,
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh = request.data.get("refresh")
    if not refresh:
        return Response(
            {"success": False, "message": "Refresh token required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh)
        token.blacklist()

        request.user.token_verified = False
        request.user.save(update_fields=["token_verified"])

        return Response(
            {"success": True, "message": "User successfully Logout"},
            status=status.HTTP_202_ACCEPTED,
        )
    except Exception:

        return Response(
            {"success": False, "message": "invalid or expired token"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def team_view(request):
    data_list = None
    if request.user.role == "ADMIN":
        data_list = User.objects.all()
    else:
        data_list = User.objects.filter(team__name=request.user.team)

    serializer = CustomUserSerializer(data_list, many=True)
    return Response({"success": True, "data": serializer.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def team_detail_view(request, reference_key):
    data = get_object_or_404(User, reference=reference_key)
    print(data)
    if data.team != request.user.team:
        return Response(
            {"success": False, "error": "data not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UserSerializer(data)
    print(serializer.data)
    return Response(
        {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
    )
