from django.contrib import admin
from .models import Timetable, Activity, Course, Activity_type, Teacher, Timetable_assignment


class TimetableAdmin(admin.ModelAdmin):
    list_display = ("id", "timetable_name", "author", "share_link")


class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "course_initials", "course_name", "course_description", "timetable")

class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type_name_pl", "type_name", "type_description", "type_color")


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher_initials", "teacher_first_name", "teacher_last_name", "teacher_link", "teacher_mail")


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "time_start", "time_end", "time_duration", "description", "timetable", "course", "activity_type")


class TimetableAssignmentsAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "timetable", "assignment_description")

# Register your models here.
admin.site.register(Timetable, TimetableAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Activity_type, ActivityTypeAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Timetable_assignment, TimetableAssignmentsAdmin)