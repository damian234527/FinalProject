from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Student

class NewAccountRegistrationForm(UserCreationForm):

    class Meta:
        model = Student
        fields = ["username", "email", "password1", "password2", "first_name", "last_name", "student_mail", "profile_description"]

class NewAccountProfileForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ["first_name", "last_name", "student_mail", "profile_description"]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=128)
    password = forms.CharField(max_length=128)