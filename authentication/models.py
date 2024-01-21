from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Student(AbstractUser):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    student_mail = models.EmailField(max_length=254, null=True, blank=True)
    profile_description = models.CharField(max_length=255, null=True, blank=True)
    active_timetable = models.ForeignKey("timetable.Timetable", on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.username