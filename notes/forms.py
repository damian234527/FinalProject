from django import forms
from django.db.models import Q
from . import models
from timetable.models import Timetable_assignment, Timetable
from django.utils import timezone

class NoteForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=models.Course.objects.none(),
                                    required=False)
    timetable = forms.ModelChoiceField(queryset=models.Timetable.objects.none(),
                                           required=False)
    set_as_public = forms.BooleanField(initial=False, required=False)
    class Meta:
        model = models.Note
        fields = ["name", "content", "course", "timetable"]
    def __init__(self, user, *args, get_time_now=False, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)

        if user:
            user_timetables_assignments = Timetable_assignment.objects.filter(Q(student_id=user.id) | Q(student_id=None))
        else:
            user_timetables_assignments = Timetable_assignment.objects.filter(student_id=None)
            user_timetables_assignments = user_timetables_assignments.values("timetable_id")
        user_timetables = Timetable.objects.filter(id__in=user_timetables_assignments)
        self.fields["timetable"].queryset = user_timetables
        user_courses = models.Course.objects.filter(timetable__id__in=user_timetables_assignments)
        self.fields["course"].queryset = user_courses

class AddExistingNoteForm(forms.Form):
     note_link = forms.UUIDField()



