import calendar
from datetime import datetime, timedelta, time
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Timetable, Activity, Activity_type, Teacher, Course, Timetable_assignment
from django.views import generic
from .forms import ActivityForm, ActivityTypesForm, TeacherForm, CourseForm, TimetableMergingForm, TimetableRenameForm, EditActivityTypeForm, ICSFileUploadForm
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from math import floor, ceil

# ======================================================MONTH======================================================

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

# ======================================================WEEK======================================================

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
            # print(f"{year} - {week}")
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
    if calendar_week[0]>calendar_week[-1]:
        second_month = calendar_week[-1].month
        return render(request, "timetable/week.html",
                      {"this_week": calendar_week,
                       "timetable_id": timetable_id,
                       "week_number": week,
                       "month": month,
                       "second_month": second_month,
                       "year": year})
    return render(request, "timetable/week.html",
                  {"this_week": calendar_week,
                   "timetable_id": timetable_id,
                   "week_number": week,
                   "day": day,
                   "month": month,
                   "year": year})

# ======================================================DAY======================================================


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

    activity_types = Activity_type.objects.filter(activity__timetable_id=timetable_id).distinct()

    # Get selected activity_types filter
    selected_activity_types = []
    form = ActivityTypesForm(request.GET)
    if form.is_valid():
        selected_activity_types  = form.cleaned_data.get("activity_types")
        # print(selected_activity_types)
    month_name = calendar.month_name[month]


    return render(request, "timetable/day.html", {
                                                                "month_name": month_name,
                                                                "timetable_id": timetable_id,
                                                                "month": month,
                                                                "day": day,
                                                                "year": year,
                                                                "activity_types": activity_types})


# ======================================================TIMETABLE======================================================

def get_available_timetables(request):
    user = None
    username = None
    user_timetables = None
    if request.user.is_authenticated:
        user = request.user.id
        username = request.user.username
        assigned_timetables = Timetable_assignment.objects.filter(student_id=user)
        user_timetables = Timetable.objects.filter(id__in=assigned_timetables.values("timetable_id"))
    not_assigned_timetables = Timetable_assignment.objects.filter(student_id=None)
    public_timetables = Timetable.objects.filter(id__in=not_assigned_timetables.values("timetable_id"))
    return render(request, "timetable/timetable_list.html",
                  {
                   "username": username,
                   "user_timetables": user_timetables,
                   "public_timetables": public_timetables})

def timetable_details(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    return render(request, "timetable/timetable_details.html", {"timetable_id": timetable_id})

def update_day(request, timetable_id, year, month, day):
    day_date = datetime(year, month, day).date()
    activity_types = Activity_type.objects.filter(activity__timetable_id=timetable_id).distinct()
    selected_activity_types = None
    if request.method == "POST":
        selected_activity_types = request.POST.getlist('activity_types', [])
    else:
        selected_activity_types = activity_types
    # timetable_times = [time(hour=9, minute=0), time(hour=9, minute=15), time(hour=9, minute=30), time(hour=9, minute=45), time(hour=10, minute=0)]
    day_activities = Activity.objects.filter(
        Q(timetable_id=timetable_id) & (Q(time_start__date=day_date) | Q(time_end__date=day_date)),
        activity_type__id__in=selected_activity_types)
    # print(selected_activity_types)
    # day_activities = Activity.objects.filter(Q(timetable_id=timetable_id) & (Q(time_start__date = day_date) | Q(time_end__date = day_date)))

    tracks = []
    track_number = None

    for activity in day_activities:
        # Checking for overlapping tracks
        overlapping_tracks = []
        for i, track_activities in enumerate(tracks):
            for track_activity in track_activities:
                if (activity.time_start < track_activity.time_end and activity.time_end > track_activity.time_start):
                    overlapping_tracks.append(i)

        # Finding the first available track for the current activity
        track_number = 0
        while track_number in overlapping_tracks:
            track_number += 1

        # Adding the current activity to the selected track
        if track_number >= len(tracks):
            tracks.append([])
        tracks[track_number].append(activity)
    # print(tracks)
    track_number = len(tracks)
    track_span = int(5 / track_number)
    if track_number != 0:
        tracks = [tracks, [], []]
        if track_number != 5:
            reserve = True
        track_end = 0
        for i in range(track_number):
            track_start = track_end + 1
            tracks[1].append(track_start)
            if reserve:
                track_end = track_start + ceil(track_span)
            else:
                track_end = track_start + floor(track_span)
            tracks[2].append(track_end)
    else:
        track_span = 1
    print(tracks[0])
    generate_time = request.GET.get("generate", True)
    if generate_time == True:
        timetable_length = 64
        timetable_times = [None] * timetable_length
        i = 0
        for hours in range(8, 24):
            for minutes in range(0, 60, 15):
                timetable_times[i] = time(hours, minutes)
                i +=1
        return render(request, "timetable/update_day.html", {
                                                                "activities_tracks": tracks,
                                                                "track_number": track_number,
                                                                "track_span": track_span,
                                                                "timetable_times": timetable_times,
                                                                "timetable_id": timetable_id,
                                                                "month": month,
                                                                "day": day,
                                                                "year": year,
                                                                "date":day_date,
                                                                "activity_types": activity_types})
    return render(request, "timetable/update_day.html", {
        "activities": tracks,
        "track_number": track_number,
        "track_span": track_span,
        "timetable_id": timetable_id,
        "month": month,
        "day": day,
        "year": year,
        "date": day_date,
        "activity_types": activity_types})

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
                author = request.user.id
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

    return render(request, "timetable/import_ics.html", {"form": upload_new_timetable_form})

def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    timetable.delete()
    return redirect("timetable:main")

def rename_timetable(request, timetable_id):
    timetable = get_object_or_404(Timetable, pk=timetable_id)
    if request.method == "POST":
        rename_form = TimetableRenameForm(request.POST, instance=timetable)
        if rename_form.is_valid():
            rename_form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
    else:
        rename_form = TimetableRenameForm(instance=timetable)
    return render(request, "timetable/rename_timetable.html", {"rename_form": rename_form})

def share_timetable(request, timetable_id):

    return render(request, "timetable/share_timetable.html")

def merge_timetable(request):
    user = request.user if request.user.is_authenticated else None
    if request.method == "POST":
        merge_timetable_form = TimetableMergingForm(user, request.POST)
        if merge_timetable_form.is_valid():
            merged_timetable_name = merge_timetable_form.cleaned_data["timetable_name"]
            merged_timetable_author = request.user
            merged_timetable = Timetable.objects.create(timetable_name=merged_timetable_name, author=merged_timetable_author)
            Timetable_assignment.objects.create(timetable=merged_timetable, student=merged_timetable_author)
            timetable1 = merge_timetable_form.cleaned_data["timetable1"]
            timetable2 = merge_timetable_form.cleaned_data["timetable2"]
            #both_timetables_activity_types = Activity_type.objects.filter(Q(timetable=timetable1) | Q(timetable=timetable2))
            #merged_timetable.activity_type.set(both_timetables_activity_types)
            #both_timetables_courses = Course.objects.filter(Q(timetable=timetable1) | Q(timetable=timetable2))
            #merged_timetable.course.set(both_timetables_courses)
            both_timetables_activities = Activity.objects.filter(Q(timetable=timetable1) | Q(timetable=timetable2))
            for activity in both_timetables_activities:
                new_activity = Activity.objects.create(time_start=activity.time_start, time_end=activity.time_end, description=activity.description, time_duration=activity.time_duration, timetable=merged_timetable, course=activity.course, activity_type=activity.activity_type)
                new_activity.teacher.set(activity.teacher.all())
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_unchanged'})
    else:
        merge_timetable_form = TimetableMergingForm(user)
    return render(request, "timetable/merge_timetable.html", {"merge_timetable_form": merge_timetable_form})

# ======================================================ACTIVITY======================================================

def add_activity(request, timetable_id):
    user = request.user if request.user.is_authenticated else None
    try:
        timetable = Timetable.objects.get(pk=timetable_id)
    except Timetable.DoesNotExist:
        raise Http404("Timetable does not exist")
    if request.method == "POST":
        create_new_activity_form = ActivityForm(user, request.POST)
        if create_new_activity_form.is_valid():
            activity = create_new_activity_form.save(commit=False)
            activity.timetable = timetable
            activity.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
    else:
        create_new_activity_form = ActivityForm(user)

    return render(request, "timetable/add_activity.html", {"activity_form": create_new_activity_form})

def edit_activity(request, timetable_id, activity_id):
    user = request.user if request.user.is_authenticated else None
    current_activity = get_object_or_404(Activity, pk=activity_id)
    if request.method == "POST":
        edit_activity_form = ActivityForm(user, request.POST, instance=current_activity)
        if edit_activity_form.is_valid():
            edit_activity_form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
    else:
        edit_activity_form = ActivityForm(user, instance=current_activity)
    return render(request, "timetable/edit_activity.html", {"activity_form": edit_activity_form})

def delete_activity(request, timetable_id, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    activity.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})

def activity_details(request, timetable_id, activity_id):
    # print(request.GET)
    activity = get_object_or_404(Activity, pk=activity_id)
    return render(request, "timetable/activity.html", {"activity": activity, "timetable_id":timetable_id})

# ======================================================TEACHER======================================================

def teacher_details(request, name_surname_initials):
    teacher = get_object_or_404(Teacher, teacher_initials=name_surname_initials)
    return render(request, "timetable/teacher.html", {"teacher": teacher})

def edit_teacher(request, name_surname_initials):
    current_teacher = get_object_or_404(Teacher, teacher_initials=name_surname_initials)
    if request.method == "POST":
        edit_teacher_form = TeacherForm(request.POST, instance=current_teacher)
        if edit_teacher_form.is_valid():
            edited_teacher = edit_teacher_form.save()
            # print(edited_teacher)
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_unchanged'})
    else:
        edit_teacher_form = TeacherForm(instance=current_teacher)

    return render(request, "timetable/edit_teacher.html", {"teacher_form": edit_teacher_form})


# ======================================================ACTIVITY_TYPE======================================================

def activity_type_details(request, activity_type_id):
    activity_type = get_object_or_404(Activity_type, pk = activity_type_id)
    return render(request, "timetable/activity_type.html", {"activity_type": activity_type})

def edit_activity_type(request, activity_type_id):
    current_activity_type = get_object_or_404(Activity_type, pk=activity_type_id)
    if request.method == "POST":
        edit_activity_type_form = EditActivityTypeForm(request.POST, instance=current_activity_type)
        if edit_activity_type_form.is_valid():
            edit_activity_type_form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
        else:
            print(edit_activity_type_form.errors)
    else:
        edit_activity_type_form = EditActivityTypeForm(instance=current_activity_type)
    return render(request, "timetable/edit_activity_type.html", {"activity_type_form": edit_activity_type_form})


# ======================================================COURSE======================================================
def course_details(request, timetable_id, course_initials):
    course = get_object_or_404(Course, course_initials = course_initials)
    return render(request, "timetable/course.html", {"course": course, "timetable_id": timetable_id})

def edit_course(request, timetable_id, course_initials):
    current_course = get_object_or_404(Course, course_initials=course_initials)
    if request.method == "POST":
        edit_course_form = CourseForm(request.POST, instance=current_course)
        if edit_course_form.is_valid():
            edit_course_form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_unchanged'})
        else:
            print(edit_course_form.errors)
    else:
        edit_course_form = CourseForm(instance=current_course)
    return render(request, "timetable/edit_course.html", {"course_form": edit_course_form})

def delete_course(request, timetable_id, course_initials):
    activity = get_object_or_404(Course, course_initials = course_initials)
    activity.delete()
    return redirect("timetable:main")