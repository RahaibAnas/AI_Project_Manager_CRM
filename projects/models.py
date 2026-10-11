from django.db import models


from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Project(models.Model):
    id = models.BigAutoField(primary_key=True,unique=True)
    name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    manager = models.ForeignKey(User,on_delete=models.CASCADE,related_name="products")
    deadline = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
