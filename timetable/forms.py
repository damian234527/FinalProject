from django import forms
from django.db.models import Q
from . import models
from django.utils import timezone

# Form used to upload .ics calendar file generated by plan.polsl.pl
class ICSFileUploadForm(forms.Form):
    ics_file = forms.FileField(label="select .ics file")
    timetable_name = forms.CharField(max_length=50, required=False)

# Activity add/edit form
class ActivityForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=models.Course.objects.none(), required=False, help_text="Course")
    activity_type = forms.ModelChoiceField(queryset=models.Activity_type.objects.none(), required=False, help_text="Activity type")

    class Meta:
        model = models.Activity
        fields = ["time_start", "time_end", "description", "course", "activity_type", "time_duration"]
        widgets = {"time_duration": forms.HiddenInput()}

    def __init__(self, user, *args, get_time_now=False, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)

        if user:
            assigned_timetables = models.Timetable_assignment.objects.filter(Q(student_id=user.id) | Q(student_id=None))
        else:
            assigned_timetables = models.Timetable_assignment.objects.filter(student_id=None)

        user_courses = models.Course.objects.filter(timetable__id__in=assigned_timetables.values("timetable_id"))
        self.fields["course"].queryset = user_courses
        self.fields["course"].choices = [(user_course.id, f"{user_course} ({user_course.timetable})") for user_course in user_courses]

        self.set_activity_type_choices(user, assigned_timetables)

        if get_time_now:
            self.fields['time_start'].initial = timezone.now()
            self.fields['time_end'].initial = timezone.now()

    def set_activity_type_choices(self, user, assigned_timetables):
        user_activities = models.Activity.objects.filter(timetable_id__in=assigned_timetables.values("timetable_id"))
        user_activity_types = models.Activity_type.objects.filter(
            Q(id__in=user_activities.values("activity_type_id")) |
            Q(type_name__in=models.Activity_type.type_names,
              type_name_pl__in=models.Activity_type.type_names_pl,
              type_color__in=models.Activity_type.type_colors)
        )
        self.fields["activity_type"].queryset = user_activity_types
        self.fields["activity_type"].choices = self.generate_activity_type_choices(user_activity_types)

    def generate_activity_type_choices(self, user_activity_types):
        choices = []
        for user_activity_type in user_activity_types:
            plans_containing_type = models.Timetable.objects.filter(
                activity__activity_type=user_activity_type
            ).distinct()

            if plans_containing_type.count() == 1:
                plan_text = f" ({plans_containing_type.first()})"
            else:
                #plan_text = " (Multiple Plans)"
                plan_text = ""

            choices.append((user_activity_type.id, f"{user_activity_type}{plan_text}"))

        return choices



class ActivityTypesForm(forms.Form):
    activity_types = forms.ModelMultipleChoiceField(
        queryset=models.Activity_type.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

class EditActivityTypeForm(forms.ModelForm):
    class Meta:
        model = models.Activity_type
        fields = ["type_name",
                  "type_name_pl",
                  "type_description",
                  "type_color"]

class TeacherForm(forms.ModelForm):
    class Meta:
        model = models.Teacher
        fields = ["teacher_first_name",
                  "teacher_last_name",
                  "teacher_link",
                  "teacher_mail"]

class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = ["course_name"]

class TimetableMergingForm(forms.Form):
    timetable_name = forms.CharField(max_length=50)
    timetable1 = forms.ModelChoiceField(queryset=models.Timetable.objects.none(),
                                        required=True, label="First timetable")
    timetable2 = forms.ModelChoiceField(queryset=models.Timetable.objects.none(),
                                        required=True, label="Second timetable")

    def __init__(self, user, *args, **kwargs):
        super(TimetableMergingForm, self).__init__(*args, **kwargs)

        # Dynamically set the queryset for timetable1 and timetable2 based on the user
        if user:
            assigned_timetables = models.Timetable_assignment.objects.filter(Q(student_id=user.id) | Q(student_id=None))
        else:
            assigned_timetables = models.Timetable_assignment.objects.filter(student_id=None)
        user_timetables = models.Timetable.objects.filter(id__in=assigned_timetables.values("timetable_id"))
        self.fields['timetable1'].queryset = user_timetables
        self.fields['timetable2'].queryset = user_timetables

class TimetableRenameForm(forms.ModelForm):
    class Meta:
        model = models.Timetable
        fields = ["timetable_name"]

class AddExistingTimetableForm(forms.Form):
     timetable_link = forms.UUIDField()

class TimetableForm(forms.Form):
    timetable = forms.ModelChoiceField(queryset=models.Timetable.objects.none(),
                                        required=True, label="Select active timetable")
    def __init__(self, user, *args, **kwargs):
        current_timetable = kwargs.pop("current_timetable", None)
        super(TimetableForm, self).__init__(*args, **kwargs)
        if user:
            assigned_timetables = models.Timetable_assignment.objects.filter(Q(student_id=user.id) | Q(student_id=None))
        else:
            assigned_timetables = models.Timetable_assignment.objects.filter(student_id=None)
        user_timetables = models.Timetable.objects.filter(id__in=assigned_timetables.values("timetable_id"))
        self.fields["timetable"].queryset = user_timetables
        if not self.is_bound and current_timetable:
            self.initial["timetable"] = current_timetable
            # print(isinstance(current_timetable, models.Timetable))