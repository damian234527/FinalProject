from django.urls import path
from .views import register, log_in, log_out

urlpatterns = [
    path("register/", register),
    path("login/", log_in),
    path("logout/", log_out),
]
