from django.urls import path
from . import views

app_name = "authentication"
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.log_in, name="log_in"),
    path("logout/", views.log_out, name="log_out"),
    path("user/<slug:username>/", views.user_profile, name="user_profile"),
    path("user/<slug:username>/update", views.get_user_data, name="update_profile"),
    path("user/<slug:username>/edit/", views.edit_profile, name="edit_profile"),
    path("user/<slug:username>/change_password/", views.change_password, name="change_password"),
]
