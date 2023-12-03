from django.urls import path
from . import views

app_name = "timetable"
urlpatterns = [
    path("timetable/", views.TimetableListView.as_view(), name="main"),
    path("timetable/<int:timetable_id>/", views.timetable_details, name="details"),
    path("timetable/<int:timetable_id>/month/", views.display_month, name="display_current_month"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/", views.display_month, name="display_month"),
    path("timetable/<int:timetable_id>/<int:year>/W<int:week>/", views.display_week, name="display_week"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/<int:day>/", views.display_day, name="display_day"),

    #path("timetable/<int:timetable_id>/month/", views.month, name="month"),
    # path("timetable/<int:timetable_id>/week/", views.week, name="week"),
    # path("timetable/<int:timetable_id>/day/", views.day, name="day"),
]
