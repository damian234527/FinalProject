from django.contrib import admin
from .models import Note, Note_assignment

# Register your models here.
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "content", "author", "course", "timetable", "date_created", "date_modified", "is_active", "share_link")

class NoteAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "note")

admin.site.register(Note, NoteAdmin)
admin.site.register(Note_assignment, NoteAssignmentAdmin)