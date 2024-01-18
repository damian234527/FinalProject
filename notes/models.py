from django.db import models
from authentication.models import Student
from timetable.models import Course, Timetable
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver


class Note(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)
    timetable = models.ForeignKey(Timetable, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    share_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class Note_assignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)

@receiver(post_save, sender=Note)
def assign_note_to_assignment(sender, instance, created, **kwargs):
    if created:
        student = instance.author
        note_assignment = Note_assignment.objects.create(student=student, note=instance)
post_save.connect(assign_note_to_assignment, sender=Note)