from django.urls import path
from . import views

app_name = "timetable"
urlpatterns = [
    path("timetable/", views.TimetableView.as_view(), name="main"),
    path("timetable/<int:timetable_id>/", views.timetable_details, name="details"),
    path("timetable/<int:timetable_id>/month/<int:year>/<int:month>/", views.display_month, name="display_month"),
    path("timetable/<int:timetable_id>/month/", views.month, name="month"),
    path("timetable/<int:timetable_id>/week/", views.week, name="week"),
    path("timetable/<int:timetable_id>/day/", views.day, name="day"),
]
