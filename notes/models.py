from django.db import models
from authentication.models import Student
from timetable.models import Course

class Note(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class Note_assignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
