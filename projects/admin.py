from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Project


# Register your models here.
@admin.register(Project)
class FlashSalesAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "client_name",
        "manager",
        "deadline"
    ]
    list_filter = [
        "name",
        "deadline",
        "manager"
    ]
    ordering = ["name","-created_at"]
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Check if the foreign key field is the 'manager' field
        if db_field.name == "manager":
          # Filter choices to only include users with the MANAGER role
          kwargs["queryset"] = User.objects.filter(role="MANAGER")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    