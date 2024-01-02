from django.urls import path
from . import views

app_name = "timetable"
urlpatterns = [
    path("timetable/", views.get_available_timetables, name="main"),
    path("timetable/import/", views.upload_new_timetable, name="import_ics_file"),
    path("timetable/merge/", views.merge_timetable, name="merge_timetable"),
    path("timetable/add/", views.add_existing_timetable, name="add_existing_timetable"),
    path("timetable/<int:timetable_id>/", views.timetable_details, name="details"),

    # display_month
    path("timetable/<int:timetable_id>/month/", views.display_month, name="display_current_month"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/", views.display_month, name="display_month"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/statistics/", views.month_stats, name="month_stats"),
    path("timetable/<int:timetable_id>/<int:year>/M/", views.display_month, name="display_month_for_week"),

    # display_week
    path("timetable/<int:timetable_id>/week/", views.display_week, name="display_current_week"),
    path("timetable/<int:timetable_id>/<int:year>/W<int:week>/", views.display_week, name="display_week"),
    path("timetable/<int:timetable_id>/<int:year>/W<int:week>/statistics/", views.week_stats, name="week_stats"),
    path("timetable/<int:timetable_id>/<int:year>/W/", views.display_week, name="display_week_for_day"),

    # display_day
    path("timetable/<int:timetable_id>/day/", views.display_day, name="display_current_day"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/<int:day>/", views.display_day, name="display_day"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/<int:day>/statistics/", views.day_stats, name="day_stats"),
    path("timetable/<int:timetable_id>/<int:year>/<int:month>/<int:day>/update/", views.update_day, name="update_day"),

    # timetable list actions
    path("timetable/<int:timetable_id>/delete/", views.delete_timetable, name="delete_timetable"),
    path("timetable/<int:timetable_id>/delete/", views.remove_timetable, name="remove_timetable"),
    path("timetable/<int:timetable_id>/rename/", views.rename_timetable, name="rename_timetable"),
    path("timetable/<int:timetable_id>/share/", views.share_timetable, name="share_timetable"),
    path("timetable/<int:timetable_id>/publish/", views.publish_timetable, name="publish_timetable"),

    # change_displayed_calendar
    # path("timetable/change/<int:timetable_id>/<str:change_val>/<int:year>/<int:month>/", views.change_displayed_calendar, name="change_month"),
    # path("timetable/change/<int:timetable_id>/<str:change_value>/<int:year>/<int:week>/", views.change_displayed_calendar, name="change_week"),
    # path("timetable/change/<int:timetable_id>/<str:change_value>/<int:year>/<int:month>/<int:day>/", views.change_displayed_calendar, name="change_day"),

    # for pop-up details windows
    path("timetable/teacher/<slug:name_surname_initials>/", views.teacher_details, name="teacher_details"),
    path("timetable/<int:timetable_id>/activity/<int:activity_id>/", views.activity_details, name="activity_details"),
    path("timetable/atype/<int:activity_type_id>/", views.activity_type_details, name="activity_type_details"),
    path("timetable/<int:timetable_id>/course/<str:course_initials>/", views.course_details, name="course_details"),

    # add or edit
    path("timetable/<int:timetable_id>/activity/add/", views.add_activity, name="add_activity"),
    path("timetable/<int:timetable_id>/activity/<int:activity_id>/edit/", views.edit_activity, name="edit_activity"),
    path("timetable/<int:timetable_id>/activity/<int:activity_id>/delete/", views.delete_activity, name="delete_activity"),

    path("timetable/atype/<int:activity_type_id>/edit/", views.edit_activity_type, name="edit_activity_type"),

    path("timetable/<int:timetable_id>/course/<str:course_initials>/edit/", views.edit_course, name="edit_course"),
    path("timetable/<int:timetable_id>/course/<str:course_initials>/delete/", views.delete_course, name="delete_course"),

    path("timetable/teacher/<slug:name_surname_initials>/edit", views.edit_teacher, name="edit_teacher"),

]
