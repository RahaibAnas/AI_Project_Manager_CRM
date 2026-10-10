from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class CustomAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_verified = validated_token.get("token_verified")
        if token_verified != user.token_verified:
            raise AuthenticationFailed("Access Token Revoked")

        return user


