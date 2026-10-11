from rest_framework import serializers

from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.StringRelatedField()
    class Meta:
        model = Project 
        fields = "__all__"
        read_only_fields = ["id"]
        extra_kwargs = {
            "name":{"required":True,"min_length":3},
            "client_name":{"required":True,"min_length":3},
            "description":{"required":True,"min_length":3},
            "manager":{"required":True},
            "deadline":{"required":True},
        }


class CutomProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    client_name = serializers.CharField()
    manager = serializers.CharField()



