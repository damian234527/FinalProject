from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Student(AbstractUser):
    # first_name = models.CharField(max_length=100)
    # last_name = models.CharField(max_length=100)
    student_mail = models.EmailField(max_length=254, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)