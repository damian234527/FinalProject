import calendar
from datetime import datetime

from django.shortcuts import render

# calendar for current month
now = datetime.now()
current_year, current_month, current_day = now.year, now.month, now.day

# month calendar
calendar_current_month = calendar.monthcalendar(current_year, current_month)
calendar_last_month_last_week = calendar.monthcalendar(current_year, current_month - 1)[-1]
next_month_days_iterator = 1

for i, day_month in enumerate(calendar_current_month[0]):
    if day_month == 0:
        calendar_current_month[0][i] = calendar_last_month_last_week[i]
for i, day_month in enumerate(calendar_current_month[-1]):
    if day_month == 0:
        calendar_current_month[-1][i] = next_month_days_iterator
        next_month_days_iterator += 1

# week calendar
week_number = current_day // 7
if current_day > calendar_current_month[week_number][0] + 6:
    week_number += 1
calendar_current_week = calendar_current_month[week_number]

# Create your views here.
def index(request):
    return render(request, "timetable/index.html")


def month(request):
    return render(request, "timetable/month.html", {"this_month": calendar_current_month,
                                                    "this_week": calendar_current_week,
                                                    "this_week_number": week_number,
                                                    "today": current_day})

def week(request):
    return render(request, "timetable/week.html", {"this_week": calendar_current_week,
                                                   "today": day})

def day(request):
    time_array = [None] * 64
    time_earliest_start = 800
    start_time = 800
    end_time = 1200
    description = ["Jerzy Respondek", "830", "lab"]
    time_to_index_conversion = (((start_time - time_earliest_start) // 100 * 60) + (start_time % 100)) // 15
    time_array[time_to_index_conversion] = [start_time, end_time, description]

    return render(request, "timetable/day.html", {"today": current_day,
                                                  "time_array": time_array,
                                                  "month": current_month,
                                                  "year": current_year})
