from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from .models import Student
from .forms import NewAccountRegistrationForm, ProfileForm, LoginForm, ChangePasswordForm


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
        #new_user_profile_form = NewAccountProfileForm()

    return render(request, "authentication/register.html", {"registration_form": create_new_user_form})

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

def get_user_data(request, username):
    student = get_object_or_404(Student, username=username)
    return render(request, "authentication/user_data.html", {"student": student})

def user_profile(request, username):
    get_user_data(request, username)
    return render(request, "authentication/user_profile.html", {"username": username})

def edit_profile(request, username):
    current_profile = get_object_or_404(Student, username=username)
    if request.method == "POST":
        edit_form = ProfileForm(request.POST, instance=current_profile)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'profile_changed'})
    else:
        edit_form = ProfileForm(instance=current_profile)
    return render(request, "authentication/edit_profile.html", {"edit_form": edit_form})


def change_password(request, username):
    current_profile = get_object_or_404(Student, username=username)

    if request.method == "POST":
        password_form = ChangePasswordForm(request.POST)
        if password_form.is_valid():
            new_password1 = password_form.cleaned_data["new_password"]
            new_password2 = password_form.cleaned_data["new_password_confirm"]

            if new_password1 == new_password2:
                current_password = password_form.cleaned_data["current_password"]
                if check_password(current_password, current_profile.password):
                    current_profile.password = new_password1
                    current_profile.save()
                    messages.success(request, 'Password changed successfully.')
                    return HttpResponse(status=204, headers={'HX-Trigger': 'profile_changed'})
                else:
                    messages.error(request, 'Invalid current password.')
            else:
                messages.warning(request, 'New passwords do not match.')
        else:
            for field, errors in password_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        password_form = ChangePasswordForm()

    return render(request, "authentication/change_password.html", {"change_password_form": password_form})