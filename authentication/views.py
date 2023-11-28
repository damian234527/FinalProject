from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from dateutil.parser import parse
from .models import Student
from .forms import NewAccountRegistrationForm, NewAccountProfileForm, LoginForm
# from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def register(request):
    if request.method == "POST":
        create_new_user_form = NewAccountRegistrationForm(request.POST)

        # Checking if passwords match
        if create_new_user_form.is_valid():
            password = create_new_user_form.cleaned_data["password1"]
            password_confirmation = create_new_user_form.cleaned_data["password2"]
            if password != password_confirmation:
                messages.error(request, "Passwords do not match.")
                return redirect("authentication:register")

            # Checking if student mail is in polsl.pl domain
            student_mail = create_new_user_form.cleaned_data.get("student_mail", "")
            if student_mail and not student_mail.endswith("polsl.pl"):
                messages.error(request, "Student mail must be in polsl.pl domain.")
                return redirect("authentication:register")

            #Creating new user
            user = create_new_user_form.save(commit=False)
            user.set_password(password)
            user.save()

            messages.success(request, "Registration completed. You can now log in.")
            return redirect("authentication:log_in")

    else:
        create_new_user_form = NewAccountRegistrationForm()
        new_user_profile_form = NewAccountProfileForm()

    return render(request, "authentication/register.html", {"registration_form": create_new_user_form,
                                                            "profile_form": new_user_profile_form})

def log_in(request):
    if request.user.is_authenticated:
        return redirect("home:page")
    if request.method == "POST":
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            user = authenticate(request,
                                username=login_form.cleaned_data.get("username"),
                                password=login_form.cleaned_data.get("password"))

            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully")
                return redirect("home:page")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        login_form = LoginForm()

    return render(request, "authentication/login.html", {"login_form": login_form})


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect("home:page")