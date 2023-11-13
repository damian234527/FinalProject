from django.shortcuts import render, redirect
from django.contrib import messages
import calendar
import icalendar
from datetime import datetime
from dateutil.parser import parse
from timetable.models import Activity, Timetable
from timetable.forms import ICSFileUploadForm
# from django.http import HttpResponse

placeholder_value = 1
# Create your views here.
def index(request):

    #calendar for current month
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    calendar_current_month = calendar.monthcalendar(year, month)

    return render(request, "home/index.html", {"calendar": calendar_current_month})

def upload_new_timetable(request):
    if request.method == "POST":
        upload_new_timetable_form = ICSFileUploadForm(request.POST, request.FILES)
        if upload_new_timetable_form.is_valid():
            ics_file = upload_new_timetable_form.cleaned_data["ics_file"] # normalizes input to be always consistent
            uploaded_filename = ics_file.name
            timetable_name = request.POST.get("timetable_name", uploaded_filename)
            timetable, created = Timetable.objects.get_or_create(name=timetable_name)

            try:
                imported_calendar = icalendar.Calendar.from_ical(ics_file.read())
                for activity in imported_calendar.walk("vevent"):
                    time_start = activity.get("dtstart").dt
                    time_end = activity.get("dtend").dt
                    description = activity.get("summary")

                    # edit
                    time_duration = placeholder_value #CHANGE
                    course = placeholder_value #CHANGE
                    activity_type = placeholder_value

                    Activity.objects.create(time_start=time_start,
                                            time_end=time_end,
                                            description=description,
                                            time_duration=time_duration,
                                            timetable=timetable,
                                            course=course,
                                            activity_type=activity_type)
                messages.success(request, ".ics file uploaded successfully.")
                return redirect("timetable")
            except Exception as upload_error:
                messages.error(request, f"An error occurred while uploading the file: {str(upload_error)}.")
    else:
        upload_new_timetable_form = ICSFileUploadForm()

    return render(request, "home/import_ics.html", {"form": upload_new_timetable_form})


