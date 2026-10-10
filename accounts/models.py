from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email,password=None,**kwargs):
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email=email)
        user = self.model(email=email,**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email,password=None,**kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser",True)
        kwargs.setdefault("is_active",True)
        return self.create_user(email,password,**kwargs)

class User(AbstractUser):
    class UserRole(models.TextChoices):
        admin = "ADMIN", "ADMIN"
        manager = "MANAGER", "MANAGER"
        agent = "AGENT", "AGENT" 

    email = models.EmailField(max_length=200,unique=True)
    name = models.CharField(max_length=200,blank=True,null=True)
    role = models.CharField(max_length=200,default=UserRole.agent,choices= UserRole.choices)
    specialization = models.TextField(blank=True,null=True)
    skills = models.JSONField(default=list)
    reference = models.CharField(max_length=10,null=True,blank=True)
    token_verified = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        # Save first so that self.id is generated if it's a new instance
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Generate reference dynamically after the ID exists
        if is_new or not self.reference:
            prefix_map = {
              self.UserRole.admin: "AD",
              self.UserRole.manager: "MA",
              self.UserRole.agent: "AG",
          }
            prefix = prefix_map.get(self.role, "AG")
            self.reference = f"{prefix}-{self.pk}"
            # Save only the reference field to avoid infinite loops
            type(self).objects.filter(pk=self.pk).update(reference=self.reference)

    def __str__(self):
        return self.email if not self.name else self.name
