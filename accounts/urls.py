from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import register, login, profile, logout

urlpatterns = [
    path("register/", register, name="register"), #post admin
    path("login/", login, name="login"), #post everyone
    path("logout/", logout, name="logout"), #post everyone auth
    path("profile/", profile, name="profile"), #get everyone auth
    path("token/refresh/", TokenRefreshView.as_view(), name="Token_refresh_view"), #everyone auth
]
