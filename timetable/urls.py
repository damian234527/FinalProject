from django.urls import path
from .views import index, month, week, day

urlpatterns = [
    path("timetable/", index),
    path("timetable/month/", month),
    path("timetable/week/", week),
    path("timetable/day/", day),
]
