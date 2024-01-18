import calendar
from datetime import datetime, timedelta, time
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Sum
from django.http import HttpResponse, Http404
from django.contrib import messages
from .models import Timetable, Activity, Activity_type, Teacher, Course, Timetable_assignment
from .forms import ActivityForm, ActivityTypesForm, TeacherForm, CourseForm, TimetableMergingForm, TimetableRenameForm, EditActivityTypeForm, ICSFileUploadForm, AddExistingTimetableForm

def check_access_permission(view_func):
    def _wrapped_view(request, *args, **kwargs):
        timetable_id = kwargs.get('timetable_id')
        user = request.user if request.user.is_authenticated else None
        access = None
        if user:
            access = Timetable_assignment.objects.filter(Q(timetable_id=timetable_id, student=user) | Q(timetable_id=timetable_id, student=None)).exists()
        else:
            access = Timetable_assignment.objects.filter(timetable_id=timetable_id, student=None).exists()
        if access:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No permission to view this timetable")
            return redirect("timetable:main")
    return _wrapped_view


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

@check_access_permission
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
    first_day = datetime(year, month, 1)
    weeks_in_month = [None] * len(calendar_month)
    weeks_in_month[0] = first_day.isocalendar()[1]
    for i in range(1, len(calendar_month)):
        weeks_in_month[i] = weeks_in_month[i-1] + 1
    if weeks_in_month[-1] == 53:
        weeks_in_month[-1] = 1
    #For setting current week
    if current_month or (month == current_date.month and year == current_date.year):
        day = current_date.day
        week_number = (day - 1) // 7 + 1
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
                       "today": current_date.day,
                       "weeks_in_month": weeks_in_month})
    return render(request, "timetable/month.html",
                  {"this_month": calendar_month,
                   "timetable_id": timetable_id,
                   "month_name": month_name,
                   "month": month,
                   "year": year,
                   "weeks_in_month": weeks_in_month})

def month_stats(request, timetable_id, year, month):
    start_date = datetime(year, month, 1)
    if month != 12:
        end_date = datetime(year, month + 1, 1)
    else:
        end_date = datetime(year + 1, 1, 1)
    # Total number of activities
    total_activities = Activity.objects.filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date).count()
    # Total duration of activities
    total_duration = Activity.objects.filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date).aggregate(Sum('time_duration'))['time_duration__sum']
    # Number and duration of activities by each activity_type
    activity_type_summary = (
        Activity.objects
        .filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date)
        .values('activity_type__type_name')
        .annotate(
            activity_count=Count('id'),
            total_duration=Sum('time_duration')
        )
    )
    return render(request, "timetable/month_stats.html", {"activities_total": total_activities, "activities_duration":total_duration, "activity_types": activity_type_summary})

# ======================================================WEEK======================================================
@check_access_permission
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
    activity_types = Activity_type.objects.filter(activity__timetable_id=timetable_id).distinct()
    return render(request, "timetable/week.html",
                  {"timetable_id": timetable_id,
                   "week_number": week,
                   "year": year,
                   "activity_types": activity_types})

def week_stats(request, timetable_id, year, week):
    # Assuming 'year' and 'week' are parameters in your URL
    start_date = datetime.strptime(f'{year}-{week}-1', "%Y-%W-%w").replace()
    end_date = start_date + timedelta(days=7)
    total_activities = Activity.objects.filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date).count()
    total_duration = Activity.objects.filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date).aggregate(Sum('time_duration'))['time_duration__sum']
    activity_type_summary = (
        Activity.objects
        .filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date)
        .values('activity_type__type_name')
        .annotate(
            activity_count=Count('id'),
            total_duration=Sum('time_duration')
        )
    )
    return render(request, "timetable/week_stats.html", {"activities_total": total_activities, "activities_duration":total_duration, "activity_types": activity_type_summary})


# ======================================================DAY======================================================

@check_access_permission
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

def day_stats(request, timetable_id, year, month, day):
    start_date = datetime(int(year), int(month), int(day))
    end_date = start_date + timedelta(days=1)
    total_activities = Activity.objects.filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date).count()
    total_duration = Activity.objects.filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date).aggregate(Sum('time_duration'))['time_duration__sum']
    activity_type_summary = (
        Activity.objects
        .filter(timetable_id=timetable_id, time_start__gte=start_date, time_end__lt=end_date)
        .values('activity_type__type_name')
        .annotate(
            activity_count=Count('id'),
            total_duration=Sum('time_duration')
        )
    )
    return render(request, "timetable/day_stats.html", {"activities_total": total_activities, "activities_duration":total_duration, "activity_types": activity_type_summary})

# ======================================================TIMETABLE======================================================

def user_timetables(request):
    if request.user.is_authenticated:
        assigned_timetables = Timetable_assignment.objects.filter(student_id=request.user.id)
        user_timetables = Timetable.objects.filter(id__in=assigned_timetables.values("timetable_id"))
        return render(request, "timetable/timetable_list_private.html", {"user_timetables": user_timetables})

def public_timetables(request):
    not_assigned_timetables = Timetable_assignment.objects.filter(student_id=None)
    public_timetables = Timetable.objects.filter(id__in=not_assigned_timetables.values("timetable_id"))
    return render(request, "timetable/timetable_list_public.html", {"public_timetables": public_timetables})

def get_available_timetables(request):
    #if request.user.is_authenticated:
        #user_timetables(request)
    #public_timetables(request)
    return render(request, "timetable/timetable_list.html")

@check_access_permission
def timetable_details(request, timetable_id):
    # timetable = get_object_or_404(Timetable, pk=timetable_id)
    return render(request, "timetable/timetable_details.html", {"timetable_id": timetable_id})

@check_access_permission
def update_day(request, timetable_id, year, month, day):
    day_date = datetime(year, month, day).date()
    generate_time = request.GET.get("generate", True)
    if generate_time == "False":
        generate_time = False
    selected_activity_types = request.GET.get("types", None)
    if selected_activity_types:
        selected_activity_types = eval(selected_activity_types)
    else:
        activity_types = Activity_type.objects.filter(activity__timetable_id=timetable_id).distinct()
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
    tracks_width = [None] * 5
    if track_number == 1 or track_number == 0:
        tracks_width = [5, 0, 0, 0, 0]
    elif track_number == 2:
        tracks_width = [3, 2, 0, 0, 0]
    elif track_number == 3:
        tracks_width = [2, 2, 1, 0, 0]
    elif track_number == 4:
        tracks_width = [2, 1, 1, 1, 0]
    else:
        tracks_width = [1, 1, 1, 1, 1]

    # print(tracks[0])
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
                                                            "timetable_times": timetable_times,
                                                            "timetable_id": timetable_id,
                                                            "month": month,
                                                            "day": day,
                                                            "year": year,
                                                            "date":day_date,
                                                            "generate_time": generate_time,
                                                            "tracks_width": tracks_width})

@check_access_permission
def update_week(request, timetable_id, year, week):
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    start_date = datetime(year, 1, 1)
    if start_date.weekday() <= 3:
        days_to_add = (week - 1) * 7 - start_date.weekday()
    else:
        days_to_add = week * 7 - start_date.weekday()
    first_day_of_week = start_date + timedelta(days=days_to_add)
    last_day_of_week = start_date + timedelta(days=days_to_add+6)
    calendar_week = [(first_day_of_week + timedelta(days=i)).day for i in range(7)]
    day = first_day_of_week.day
    month = first_day_of_week.month
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    today = None
    activity_types = list(Activity_type.objects.filter(activity__timetable_id=timetable_id).values_list('id', flat=True).distinct())
    if request.method == "POST":
        selected_activity_types = request.POST.getlist('activity_types', [])
    else:
        selected_activity_types = activity_types
    # print(selected_activity_types)
    if calendar_week[0]>calendar_week[-1]:
        second_month = last_day_of_week.month
        if (month == current_month and year == current_year) or (
                second_month == current_month and year == current_year):
            today = current_date.day
        return render(request, "timetable/update_week.html",
                      {"this_week": calendar_week,
                       "timetable_id": timetable_id,
                       "day": day,
                       "month": month,
                       "second_month": second_month,
                       "year": year,
                       "today": today,
                       "selected_activity_types": selected_activity_types,
                       "week_days": week_days})
    if month == current_month and year == current_year:
        today = current_date.day
    return render(request, "timetable/update_week.html", {"this_week": calendar_week,
                            "timetable_id": timetable_id,
                            "day": day,
                            "month": month,
                            "year": year,
                            "today": today,
                            "selected_activity_types": selected_activity_types,
                            "week_days": week_days})

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

@check_access_permission
def delete_timetable(request, timetable_id):
    try:
        timetable = get_object_or_404(Timetable, pk=timetable_id)
        timetable.delete()
    except Exception as e:
        messages.error(request, "Something went wrong when removing timetable", e)
    return redirect("timetable:main")

@check_access_permission
def remove_timetable(request, timetable_id):
    try:
        if request.user:
            timetable_assignment = get_object_or_404(Timetable_assignment, timetable_id=timetable_id, student=request.user.id)
            timetable_assignment.delete()
    except Exception as e:
        messages.error(request, "Something went wrong when removing timetable", e)
    return redirect("timetable:main")

@check_access_permission
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

@check_access_permission
def share_timetable(request, timetable_id):
    timetable = Timetable.objects.get(pk=timetable_id)
    share_link = timetable.share_link
    author = timetable.author
    return render(request, "timetable/share_timetable.html", {"share_link": share_link, "author": author, "timetable_id": timetable_id})

@check_access_permission
def publish_timetable(request, timetable_id):
    try:
        current_timetable_assignments = Timetable_assignment.objects.filter(timetable_id=timetable_id)
        current_timetable_assignments.delete()
        public_timetable_assignment = Timetable_assignment.objects.create(timetable_id=timetable_id, student_id=None)
    except Exception as e:
        messages.error(request, "Something went wrong when publishing timetable", e)
        return redirect("timetable:main")
    messages.success(request, "Timetable published")
    return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
    #return redirect("timetable:main")

def add_existing_timetable(request):
    user = request.user if request.user.is_authenticated else None
    if user:
        if request.method == "POST":
            add_timetable_form = AddExistingTimetableForm(request.POST)
            if add_timetable_form.is_valid():
                entered_link = add_timetable_form.cleaned_data["timetable_link"]
                timetable = get_object_or_404(Timetable, share_link=entered_link)
                try:
                    Timetable_assignment.objects.create(timetable=timetable, student=user)
                except:
                    if Timetable_assignment.objects.filter(timetable=timetable, student=user).exists():
                        messages.warning(request, "Given timetable already added")
                    else:
                        messages.error(request, "Something went wrong")
                messages.success(request, "Timetable added successfully")
                return HttpResponse(status=204)
        else:
            add_timetable_form = AddExistingTimetableForm()
        return render(request, "timetable/add_existing_timetable.html", {"add_timetable_form": add_timetable_form})

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
            return HttpResponse(status=204)
    else:
        merge_timetable_form = TimetableMergingForm(user)
    return render(request, "timetable/merge_timetable.html", {"merge_timetable_form": merge_timetable_form})

# ======================================================ACTIVITY======================================================

@check_access_permission
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
            activity.time_duration = activity.time_end - activity.time_start
            activity.timetable = timetable
            activity.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
    else:
        create_new_activity_form = ActivityForm(user, get_time_now=True)

    return render(request, "timetable/add_activity.html", {"activity_form": create_new_activity_form})

@check_access_permission
def edit_activity(request, timetable_id, activity_id):
    user = request.user if request.user.is_authenticated else None
    current_activity = get_object_or_404(Activity, pk=activity_id)
    if request.method == "POST":
        edit_activity_form = ActivityForm(user, request.POST, instance=current_activity)
        if edit_activity_form.is_valid():
            activity = edit_activity_form.save(commit=False)
            activity.time_duration = current_activity.time_end - current_activity.time_start
            activity.save()
            messages.success(request, "Activity edited successfully")
            return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
        else:
            messages.error(request, "Something went wrong when editing activity")
    else:
        edit_activity_form = ActivityForm(user, get_time_now=True, instance=current_activity)

    return render(request, "timetable/edit_activity.html", {"activity_form": edit_activity_form})

@check_access_permission
def delete_activity(request, timetable_id, activity_id):
    try:
        activity = get_object_or_404(Activity, pk=activity_id)
        activity.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
    except Exception as e:
        messages.error(request, "Something went wrong when deleting activity: ", e)

@check_access_permission
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
            return HttpResponse(status=204)
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
            messages.error(request, "Something went wrong: ", edit_activity_type_form.errors)
    else:
        edit_activity_type_form = EditActivityTypeForm(instance=current_activity_type)
    return render(request, "timetable/edit_activity_type.html", {"activity_type_form": edit_activity_type_form})


# ======================================================COURSE======================================================
@check_access_permission
def course_details(request, timetable_id, course_initials):
    course = get_object_or_404(Course, course_initials = course_initials)
    return render(request, "timetable/course.html", {"course": course, "timetable_id": timetable_id})

@check_access_permission
def edit_course(request, timetable_id, course_initials):
    current_course = get_object_or_404(Course, course_initials=course_initials)
    if request.method == "POST":
        edit_course_form = CourseForm(request.POST, instance=current_course)
        if edit_course_form.is_valid():
            edit_course_form.save()
            return HttpResponse(status=204)
        else:
            messages.error(request, "Something went wrong: ", edit_course_form.errors)
    else:
        edit_course_form = CourseForm(instance=current_course)
    return render(request, "timetable/edit_course.html", {"course_form": edit_course_form})

@check_access_permission
def delete_course(request, timetable_id, course_initials):
    try:
        activity = get_object_or_404(Course, course_initials = course_initials)
        activity.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'timetable_changed'})
    except Exception as e:
        messages.error(request, "Something went wrong when deleting course: ", e)

