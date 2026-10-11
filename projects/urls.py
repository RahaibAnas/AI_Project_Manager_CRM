from django.urls import path

from .views import project_view,project_detail_view,project_tasks_view

urlpatterns = [
    path("",project_view),
    path("<int:pk>/",project_detail_view),
    path("<int:pk>/tasks/",project_tasks_view)
]