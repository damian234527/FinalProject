from django.urls import path
from . import views

app_name = "timetable"
urlpatterns = [
    path("timetable/", views.TimetableListView.as_view(), name="main"),
    path("timetable/<int:timetable_id>/", views.timetable_details, name="details"),

    # display_month
    path("timetable/<int:timetable_id>/month/", views.display_month, name="display_current_month"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/", views.display_month, name="display_month"),

    # display_week
    path("timetable/<int:timetable_id>/week/", views.display_week, name="display_current_week"),
    path("timetable/<int:timetable_id>/<int:year>/W<int:week>/", views.display_week, name="display_week"),

    # display_day
    path("timetable/<int:timetable_id>/day/", views.display_day, name="display_current_day"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/<int:day>/", views.display_day, name="display_day"),

    path("timetable/delete/<int:timetable_id>/", views.delete_timetable, name="delete_timetable"),
    path("timetable/rename/<int:timetable_id>/", views.rename_timetable, name="rename_timetable"),

    # change_displayed_calendar
    path("timetable/change/<int:timetable_id>/<str:change_val>/<int:year>/<int:month>/", views.change_displayed_calendar, name="change_month"),
    path("timetable/change/<int:timetable_id>/<str:change_value>/<int:year>/<int:week>/", views.change_displayed_calendar, name="change_week"),
    path("timetable/change/<int:timetable_id>/<str:change_value>/<int:year>/<int:month>/<int:day>/", views.change_displayed_calendar, name="change_day"),

    # for pop-up details windows
    path("timetable/<slug:name_surname_initials>", views.teacher_details, name="teacher_details"),
    path("timetable/<int:activity_id>", views.activity_details, name="activity_details"),
    path("timetable/<slug:activity_type_name>", views.activity_type_details, name="activity_type_details"),
    path("timetable/<slug:course_initials>", views.course_details, name="course_details"),
]
