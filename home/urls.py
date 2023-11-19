from django.urls import path
from .views import index, upload_new_timetable

app_name = "home"
urlpatterns = [
    path("", index, name="page"),
    path("import/", upload_new_timetable, name="import_ics_file")
]
