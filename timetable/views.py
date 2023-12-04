import calendar
from datetime import datetime, timedelta
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from .models import Timetable
from django.views import generic



class TimetableListView(generic.ListView):
    template_name = "timetable/TimetableView.html"
    context_object_name = "available_timetables_list"
    model = Timetable
    def get_all_timetables(self):
        return Timetable.objects.all()


class TimetableDetailsView(generic.DetailView):
    def get_specific_timetable(timetable_id):
        return Timetable.objects.filter(pk=timetable_id)

def get_month_calendar(year, month):
    calendar_month = calendar.monthcalendar(year, month)
    calendar_last_month_last_week = calendar.monthcalendar(year, month - 1)[-1]
    next_month_days_iterator = 1
    for i, day_month in enumerate(calendar_month[0]):
        if day_month == 0:
            calendar_month[0][i] = calendar_last_month_last_week[i]
    for i, day_month in enumerate(calendar_month[-1]):
        if day_month == 0:
            calendar_month[-1][i] = next_month_days_iterator
            next_month_days_iterator += 1
    return calendar_month

def display_month(request, timetable_id, year=None, month=None):
    current_date = datetime.now()
    current_month = False
    if year == None and month == None:
        year = current_date.year
        month = current_date.month
        current_month = True
    # Get the month calendar for the specified year and month
    calendar_month = get_month_calendar(year, month)
    month_name = calendar.month_name[month]

    if current_month or (month == current_date.month and year == current_date.year):
        day = current_date.day
        week_number = day // 7
        if day > calendar_month[week_number][0] + 6 or calendar_month[week_number][6] < day:
            week_number += 1
        #current_week = calendar_month[week_number]

    return render(request, "timetable/month.html",
                  {"this_month": calendar_month,
                   "this_week": week_number,
                   "timetable_id": timetable_id,
                   "month_name": month_name,
                   "year": year})

def display_week(request, timetable_id, year=None, week=None):
    if year == None and week == None:
        current_date = datetime.now()
        year = current_date.year
        week = current_date.isocalendar()[1]
    start_date = datetime(year, 1, 1)
    if start_date.weekday() <= 3:
        days_to_add = (week - 1) * 7 - start_date.weekday()
    else:
        days_to_add = week * 7 - start_date.weekday()

    first_day_of_week = start_date + timedelta(days=days_to_add)
    calendar_week = [(first_day_of_week + timedelta(days=i)).day for i in range(7)]

    return render(request, "timetable/week.html",
                  {"this_week": calendar_week,
                   "timetable_id": timetable_id,
                   "week_number": week,
                   "year": year})

def display_day(request, timetable_id, year=None, month=None, day=None):
    if year == None and month == None and day==None:
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.day
    month_name = calendar.month_name[month]
    return render(request, "timetable/day.html", {
                                                    "month_name": month_name,
                                                    "timetable_id": timetable_id,
                                                    "month": month,
                                                    "day": day,
                                                    "year": year})

def timetable_details(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    return render(request, "timetable/timetable_details.html", {"timetable_id": timetable_id})



"""
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

def month(request):
    month_name = calendar.month_name[current_month]
    return render(request, "timetable/month.html", {"this_month": calendar_current_month,
                                                    "this_week": calendar_current_week,
                                                    "this_week_number": week_number,
                                                    "today": current_day,
                                                    "month_name": month_name})

def week(request):
    return render(request, "timetable/week.html", {"this_week": calendar_current_week,
                                                   "today": day})

def day(request):
    time_array = [None] * 64
    time_earliest_start = 800
    start_time = 800
    end_time = 1200
    description = ["Jerzy Respondek", "830", "lab"]
    activity = {"start_time": start_time, "end_time": end_time, "description": description}
    activities = []
    activities.append(activity)
    timetable_times = range(800, 2100, 100)
    # time_to_index_conversion = (((start_time - time_earliest_start) // 100 * 60) + (start_time % 100)) // 15
    # time_array[time_to_index_conversion] = [start_time, end_time, description]

    return render(request, "timetable/day.html", {"today": current_day,
                                                  #"time_array": time_array,
                                                  "activities": activities,
                                                  "month": current_month,
                                                  "year": current_year,
                                                  "timetable_times": timetable_times})
"""