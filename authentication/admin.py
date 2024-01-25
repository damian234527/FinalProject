from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "student_mail", "profile_description", "active_timetable", "is_staff", "is_active")

# Register your models here.
admin.site.register(Student, StudentAdmin)