from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Student

class NewAccountRegistrationForm(UserCreationForm):

    class Meta:
        model = Student
        fields = ["username", "email"]

class NewAccountProfileForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ["first_name", "last_name", "student_mail", "profile_description"]

class LoginForm(forms.Form):
    user_name = forms.CharField(max_length=128)
    user_password = forms.CharField(max_length=128)