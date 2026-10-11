from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Team

# Register your models here.
@admin.register(User)
class FlashSalesAdmin(admin.ModelAdmin):
    list_display = [
        "name","email","role","specialization","team","reference","skills"
    ]
    list_filter = [
        "role",
        "specialization",
        "team",
    ]
    ordering = ["name", "role", "reference","team"]
    list_per_page = 10

admin.site.register(Team)
