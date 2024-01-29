from django.shortcuts import render
from datetime import datetime


placeholder_value = 1
# Create your views here.
def index(request):

    #current date
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    # calendar_current_month = calendar.monthcalendar(year, month)
    return render(request, "home/index.html", {"year": year, "month": month, "day": day})


