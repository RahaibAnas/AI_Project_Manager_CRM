from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()

# Register your models here.
@admin.register(User)
class FlashSalesAdmin(admin.ModelAdmin):
    list_display = [
        "name","email","role","specialization","reference","skills"
    ]
    list_filter = [
        "role",
        "specialization",
    ]
    list_per_page = 10
