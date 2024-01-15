from django.shortcuts import render
import calendar
from datetime import datetime

placeholder_value = 1
# Create your views here.
def index(request):

    #calendar for current month
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    calendar_current_month = calendar.monthcalendar(year, month)

    return render(request, "home/index.html", {"calendar": calendar_current_month})


