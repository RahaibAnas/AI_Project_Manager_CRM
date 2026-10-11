from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Team

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    team = serializers.StringRelatedField()
    class Meta:
        model = User
        fields = [
            "reference",
            "name",
            "email",
            "team",
            "specialization",
            "skills",
            "password",
            "role",
        ]
        read_only_fields = ["id","reference"]
        extra_kwargs = {
            "email": {"required": True},
            "password": {"required": True, "write_only": True, "min_length": 3},
        }

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        name = validated_data.get("name","")

        return User.objects.create_user(
            email=email, password=password, name = name
        )

class CustomUserSerializer(serializers.Serializer):
    reference = serializers.CharField()
    name = serializers.CharField()
    team = serializers.CharField()
    role = serializers.CharField()



class TeamSerializer(serializers.Serializer):
    class Meta:
        Model = Team
        fields = "__all__"
