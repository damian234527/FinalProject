from django.urls import path
from .views import index, month, week, day

app_name = "timetable"
urlpatterns = [
    path("timetable/", index, name="main"),
    path("timetable/month/", month, name="month"),
    path("timetable/week/", week, name="week"),
    path("timetable/day/", day, name="day"),
]
