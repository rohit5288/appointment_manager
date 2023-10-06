from django.db import models
from accounts.constants import *
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username=models.CharField(unique=True,max_length=30,null=True, blank=True)
    first_name = models.CharField(max_length = 255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank= True)
    email = models.EmailField(null=True,blank=True)
    mobile_no = models.CharField(max_length=255,null=True,blank=True)
    role = models.PositiveIntegerField(choices=USER_ROLE,null=True,blank=True)
    created=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    
    class Meta:
        managed=True
        db_table = "tbl_user"

class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    speciality=models.CharField(max_length=255,null=True,blank=True)
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


class Patient(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"