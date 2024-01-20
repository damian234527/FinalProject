from django import forms
from django.db.models import Q
from . import models
from timetable.models import Timetable_assignment, Timetable
from django.utils import timezone

class NoteForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=models.Course.objects.none(),
                                    required=False)
    # timetable = forms.ModelChoiceField(queryset=models.Timetable.objects.none(), required=False, widget=forms.HiddenInput())
    # set_as_public = forms.BooleanField(initial=False, required=False)
    class Meta:
        model = models.Note
        fields = ["name", "content", "course", "timetable"]
        widgets = {"timetable": forms.HiddenInput()}
    def __init__(self, user, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)

        if user:
            user_timetables_assignments = Timetable_assignment.objects.filter(Q(student_id=user.id) | Q(student_id=None))
        else:
            user_timetables_assignments = Timetable_assignment.objects.filter(student_id=None)
            user_timetables_assignments = user_timetables_assignments.values("timetable_id")
            # self.fields["set_as_public"].initial = True
            # self.fields["set_as_public"].disabled = True
        # user_timetables = Timetable.objects.filter(id__in=user_timetables_assignments)
        # self.fields["timetable"].queryset = user_timetables
        self.fields["timetable"].required = False
        user_courses = models.Course.objects.filter(timetable__id__in=user_timetables_assignments)
        self.fields["course"].queryset = user_courses
        self.fields["course"].choices = [(user_course.id, f"{user_course} ({user_course.timetable})") for user_course in user_courses]

        selected_course_id = self.data.get("course", None)
        if selected_course_id:
            selected_course = models.Course.objects.get(id=selected_course_id)
            print(selected_course)
            print(type(selected_course.timetable))
            self.fields["timetable"].initial = selected_course.timetable
    def clean(self):
        cleaned_data = super().clean()
        selected_course = cleaned_data.get("course")

        if selected_course:
            cleaned_data["timetable"] = selected_course.timetable

        return cleaned_data

class AddExistingNoteForm(forms.Form):
     note_link = forms.UUIDField()



