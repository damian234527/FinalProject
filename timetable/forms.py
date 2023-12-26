from django import forms
from .models import Timetable, Activity_type, Course, Activity
from bootstrap_modal_forms.forms import BSModalModelForm

# Form used to upload .ics calendar file generated by plan.polsl.pl
class ICSFileUploadForm(forms.Form):
    ics_file = forms.FileField(label="select .ics file")
    timetable_name = forms.CharField(max_length=50)

# Activity add/edit form
class ActivityForm(forms.ModelForm):
    #timetable = forms.ModelChoiceField(queryset=Timetable.objects.all(), required=False, help_text="Timetable")
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False, help_text="Course")
    activity_type = forms.ModelChoiceField(queryset=Activity_type.objects.all(), required=False, help_text="Activity type")
    class Meta:
        model = Activity
        fields = ["time_start", "time_end", "description", "course", "activity_type"]

class ActivityTypeForm(forms.Form):
    activity_types = forms.ModelMultipleChoiceField(
        queryset=Activity_type.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

class ActivityModelForm(BSModalModelForm):
    class Meta:
        model = Activity
        exclude = ["time_duration", "timetable"]

"""
class ActivityModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        timetable_instance = kwargs.pop('timetable_instance', None)
        super(ActivityModelForm, self).__init__(*args, **kwargs)

        # Set the initial value for the timetable field
        if timetable_instance:
            self.fields['timetable'].initial = timetable_instance

    class Meta:
        model = Activity
        exclude = ["time_duration", "timetable"]
"""