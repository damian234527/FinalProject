from django.shortcuts import render
import calendar
from datetime import datetime
from authentication.models import Student

placeholder_value = 1
# Create your views here.
def index(request):

    #calendar for current month
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    calendar_current_month = calendar.monthcalendar(year, month)
    timetable_id = 7
    return render(request, "home/index.html", {"timetable_id": timetable_id, "year": year, "month": month, "day": day})


