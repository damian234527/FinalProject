import calendar
from datetime import datetime, timedelta, time
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Timetable, Activity, Activity_type, Teacher, Course, Timetable_assignment
from django.views import generic



class TimetableListView(generic.ListView):
    template_name = "timetable/timetable_list.html"
    context_object_name = "available_timetables_list"
    model = Timetable
    def get_all_timetables(self):
        return Timetable.objects.all()
def get_available_timetables(request):
    user = None
    user_timetables = None
    if request.user.is_authenticated:
        user = request.user.id
        assigned_timetables = Timetable_assignment.objects.filter(student_id=user)
        user_timetables = Timetable.objects.filter(id__in=assigned_timetables.values("timetable_id"))
    not_assigned_timetables = Timetable_assignment.objects.filter(student_id=None)
    public_timetables = Timetable.objects.filter(id__in=not_assigned_timetables.values("timetable_id"))
    return render(request, "timetable/timetable_list.html",
                  {"user": user,
                   "user_timetables": user_timetables,
                   "public_timetables": public_timetables})




class TimetableDetailsView(generic.DetailView):
    def get_specific_timetable(timetable_id):
        return Timetable.objects.filter(pk=timetable_id)

def get_month_calendar(year, month):
    calendar_month = calendar.monthcalendar(year, month)
    if month == 1:
        calendar_last_month_last_week = calendar.monthcalendar(year-1, 12)[-1]
    else:
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

    # set current date as month to be displayed
    if year == None and month == None:
        year = current_date.year
        month = current_date.month
        current_month = True

    # Get the month calendar for the specified year and month when using buttons
    if request.method == 'POST':
        change_value = request.POST.get("change_value", "0")
        change_value = int(change_value)
        if change_value != 0:
            year = year + (month + change_value - 1) // 12
            month = ((month + change_value - 1) % 12) + 1
            return redirect('timetable:display_month', timetable_id, year, month)
        week_number = int(request.POST.get("week_number", "0"))
        if week_number != 0:
            iso_date = datetime.strptime(f"{year}-W{week_number}-1","%Y-W%W-%w")
            month = iso_date.strftime("%m")
            return redirect('timetable:display_month', timetable_id, year, month)
    calendar_month = get_month_calendar(year, month)
    month_name = calendar.month_name[month]
    first_day = calendar_month[0][0]
    last_day = calendar_month[-1][-1]
    if first_day > 7:
        if month == 1:
            start_date = datetime(year-1, 12, first_day).date()
        else:
            start_date = datetime(year, month-1, first_day).date()
    else:
        start_date = datetime(year, month, first_day).date()

    if last_day <= 7:
        if month == 12:
            end_date = datetime(year+1, 1, last_day).date()
        else:
            end_date = datetime(year, month+1, last_day).date()
    else:
        end_date = datetime(year, month, last_day).date()
    month_activities = Activity.objects.filter(Q(timetable_id=timetable_id) & (Q(time_start__range = [start_date, end_date]) | Q(time_end__range = [start_date, end_date])))

    #For setting current week
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
                       "month": month,
                       "year": year,
                       "today": current_date.day})
    return render(request, "timetable/month.html",
                  {"this_month": calendar_month,
                   "timetable_id": timetable_id,
                   "month_name": month_name,
                   "month": month,
                   "year": year})

def display_week(request, timetable_id, year=None, week=None):
    if year == None and week == None:
        current_date = datetime.now()
        year = current_date.year
        week = current_date.isocalendar()[1]
    # Get the week calendar for the specified year and month when using buttons
    if request.method == 'POST':
        change_value = request.POST.get("change_value", "0")
        change_value = int(change_value)
        if change_value != 0:
            year = year + (week + change_value - 1) // 52
            week = ((week + change_value - 1) % 52) + 1
            print(f"{year} - {week}")
            return redirect('timetable:display_week', timetable_id, year, week)
        day_and_month = request.POST.get("day_and_month", "")
        if day_and_month != "":
            day, month = int(day_and_month.split("_")[0]), int(day_and_month.split("_")[1])
            date = datetime(year, month, day)
            week = date.isocalendar()[1]
            return redirect('timetable:display_week', timetable_id, year, week)
    start_date = datetime(year, 1, 1)
    if start_date.weekday() <= 3:
        days_to_add = (week - 1) * 7 - start_date.weekday()
    else:
        days_to_add = week * 7 - start_date.weekday()
    first_day_of_week = start_date + timedelta(days=days_to_add)
    calendar_week = [(first_day_of_week + timedelta(days=i)).day for i in range(7)]
    day = first_day_of_week.day
    month = first_day_of_week.month
    return render(request, "timetable/week.html",
                  {"this_week": calendar_week,
                   "timetable_id": timetable_id,
                   "week_number": week,
                   "day": day,
                   "month": month,
                   "year": year})

def display_day(request, timetable_id, year=None, month=None, day=None):
    if year == None and month == None and day==None:
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.day
    # Get the day calendar for the specified year and month when using buttons
    if request.method == 'POST':
        change_value = request.POST.get("change_value", "0")
        change_value = int(change_value)
        if change_value != 0:
            new_date = datetime(year, month, day) + timedelta(days=change_value)
            year = new_date.year
            month = new_date.month
            day = new_date.day
            return redirect('timetable:display_day', timetable_id, year, month, day)
    month_name = calendar.month_name[month]
    timetable_times = [None] * 64
    i = 0
    for hours in range(8, 24):
        for minutes in range(0, 60, 15):
            timetable_times[i] = time(hours, minutes)
            i +=1
    # timetable_times = [time(hour=9, minute=0), time(hour=9, minute=15), time(hour=9, minute=30), time(hour=9, minute=45), time(hour=10, minute=0)]
    day_date = datetime(year, month, day).date()
    day_activities = Activity.objects.filter(Q(timetable_id=timetable_id) & (Q(time_start__date = day_date) | Q(time_end__date = day_date)))
    return render(request, "timetable/day.html", {
                                                                "activities": day_activities,
                                                                "timetable_times": timetable_times,
                                                                "month_name": month_name,
                                                                "timetable_id": timetable_id,
                                                                "month": month,
                                                                "day": day,
                                                                "year": year,
                                                                "date":day_date})

def timetable_details(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    return render(request, "timetable/timetable_details.html", {"timetable_id": timetable_id})


def teacher_details(request, name_surname_initials):
    teacher = get_object_or_404(Teacher, pk=name_surname_initials)
    return render(request, "timetable/teacher.html", {"teacher": teacher})

def activity_details(request, activity_id):
    activity = get_object_or_404(Teacher, pk=activity_id)
    return render(request, "timetable/activity.html")

def activity_type_details(request, activity_type_name):
    activity_type = get_object_or_404(Activity_type, type_name = activity_type_name)
    return render(request, "timetable/activity_type.html")

def course_details(request, course_initials):
    course = get_object_or_404(Course, course_initials = course_initials)
    return render(request, "timetable/course_details.html")

def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    timetable.delete()
    return redirect("timetable:main")

def rename_timetable(request, timetable_id):
    return render(request, "timetable/rename.html")

def change_displayed_calendar(request, timetable_id, change_value, year, month, week=None, day=None):
    change_value = int(change_value)
    if day is not None:
        new_date = datetime(year, month, day).date() + timedelta(days=change_value)
        return display_day(request, timetable_id, new_date.year, new_date.month, new_date.day)
    elif week is not None:
        if week == 1 and change_value < 0:
            return display_week(request, timetable_id, year=year - 1, week=53 + change_value)
        elif week == 52 and change_value > 0:
            return display_week(request, timetable_id, year=year + 1, week=0 + change_value)
        else:
            return display_week(request, timetable_id, year=year, week=week + change_value)
    else:
        if month == 1 and change_value < 0:
            return display_month(request, timetable_id, year=year - 1, month=13 + change_value)
        elif month == 12 and change_value > 0:
            return display_month(request, timetable_id, year=year + 1, month=0 + change_value)
        else:
            return display_month(request, timetable_id, year=year, month=month + change_value)
    return 1



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