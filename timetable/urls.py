from django.urls import path
from .views import index, month, week, day, display_month

app_name = "timetable"
urlpatterns = [
    path("timetable/", index, name="main"),
    path("timetable/month/<int:year>/<int:month>/", display_month, name="display_month"),
    path("timetable/month/", month, name="month"),
    path("timetable/week/", week, name="week"),
    path("timetable/day/", day, name="day"),
]
