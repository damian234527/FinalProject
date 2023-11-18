from django.db import models
from authentication.models import Student
# Create your models here.


class Timetable(models.Model):
    timetable_name = models.CharField(max_length=255)
    author = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)


class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_initialism = models.CharField(max_length=15)
    timetable = models.ManyToManyField(Timetable)


class Activity_type(models.Model):
    type_name = models.CharField(max_length=100)
    type_description = models.CharField(max_length=255)
    type_color = models.CharField(max_length=10, default="#FFFFFF")


class Activity(models.Model):
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    description = models.CharField(max_length=255)
    time_duration = models.DurationField()
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    activity_type = models.ForeignKey(Activity_type, on_delete=models.CASCADE)


class Teacher(models.Model):
    teacher_first_name = models.CharField(max_length=100)
    teacher_last_name = models.CharField(max_length=100)
    teacher_link = models.URLField(max_length=200)
    teacher_mail = models.EmailField(max_length=254)

