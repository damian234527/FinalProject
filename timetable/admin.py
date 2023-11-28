from django.contrib import admin
from .models import Timetable, Activity, Course, Activity_type

# Register your models here.
admin.site.register(Timetable)
admin.site.register(Activity)
admin.site.register(Activity_type)
admin.site.register(Course)