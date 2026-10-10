from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "specialization",
            "skills",
            "reference",
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
