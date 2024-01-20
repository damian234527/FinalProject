from django.urls import path
from . import views

app_name = "notes"
urlpatterns = [
    path("", views.main, name="main"),
    path("<int:note_id>", views.details, name="details"),
    path("private/", views.user_notes, name="user_list"),
    path("public/", views.public_notes, name="public_list"),
    path("inactive/", views.inactive_notes, name="inactive_list"),
    path("add/", views.add_note, name="add_note"),
    path("<int:note_id>/change/", views.change_status, name="change_status"),
    path("<int:note_id>/edit/", views.edit_note, name="edit_note"),
    path("<int:note_id>/delete/", views.delete_note, name="delete_note"),
    path("<int:note_id>/remove/", views.remove_note, name="remove_note"),
    path("<int:note_id>/share/", views.share_note, name="share_note"),
    path("<int:note_id>/publish/", views.publish_note, name="publish_note"),
    path("assign/", views.assign_note, name="assign_note"),

]
