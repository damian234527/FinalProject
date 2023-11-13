from django.urls import path
from .views import index, upload_new_timetable

urlpatterns = [
    path("", index),
    path("import/", upload_new_timetable, name="import")
]
