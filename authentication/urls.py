from django.urls import path, include
from . import views

app_name = "authentication"
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.log_in, name="log_in"),
    path("logout/", views.log_out, name="log_out"),
    path("user/<int:user_id>", views.user_profile, name="user_profile"),
]
