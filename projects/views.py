from django.shortcuts import render , get_object_or_404, get_list_or_404

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAdminUser,IsAuthenticated

from .models import Project
from .serializers import ProjectSerializer, CutomProjectSerializer
from .permissions import IsAdminOrManagerOnly


# Create your views here.
@api_view(["GET"])
@permission_classes([IsAdminOrManagerOnly])
def project_view(request):
    data=None
    if request.user.role == "ADMIN":
        data = Project.objects.all()
    if request.user.role == "MANAGER":
        data = Project.objects.filter(manager=request.user.id)
    serializer = CutomProjectSerializer(data, many=True)
    return Response({
        "success":True,
        "data":serializer.data
    },status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAdminOrManagerOnly])
def project_detail_view(request,pk):
    data = get_object_or_404(Project,id=pk)
    if data.manager != request.user:
        return Response({
            "success":False,
            "error":"Data Not Found"
        },status=status.HTTP_404_NOT_FOUND)
    serializer = ProjectSerializer(data)
    return Response({
            "success":True,
            "data":serializer.data
        },status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminOrManagerOnly])
def project_tasks_view(request,pk):
    return Response(
        {"success": True, "message": "under maintance"}, status=status.HTTP_200_OK
    )
    data = get_list_or_404(Task,project=pk)
    serializer = ProjectSerializer(data)
    return Response({
            "success":True,
            "data":serializer.data
        },status=status.HTTP_200_OK)
