import sys

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
            #timetable_name = request.POST.get("timetable_name", uploaded_filename)
            timetable_name = upload_new_timetable_form.cleaned_data["timetable_name"]
            if timetable_name == "":
                uploaded_filename = ics_file.name
                timetable_name = uploaded_filename
            author = request.user.is_authenticated
            if author:
                author = author.id
            else:
                author = None
            success, message = Timetable.import_timetable(ics_file, timetable_name, author)

            if success:
                messages.success(request, message)
                return redirect("timetable:main")
            else:
                messages.error(request, message)
    else:
        upload_new_timetable_form = ICSFileUploadForm()

    return render(request, "home/import_ics.html", {"form": upload_new_timetable_form})


