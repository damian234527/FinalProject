from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from dateutil.parser import parse
from .models import Student
from .forms import CreateNewAccountForm, LoginForm
# from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def register(request):
    if request.method == "POST":
        create_new_user_form = CreateNewAccountForm(request.POST)
        if create_new_user_form.is_valid():
            # create_new_user_form
            messages.success(request, ".ics file uploaded successfully.")
            return redirect("main_page")
            # messages.error(request, f"An error occurred while uploading the file: {str(upload_error)}.")
    else:
        create_new_user_form = CreateNewAccountForm()

    return render(request, "authentication/register.html", {"form": create_new_user_form})

def log_in(request):
    if request.user.is_authenticated:
        return redirect("")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password")
            )
            if user is not None:
                login(request, user)
                return redirect("view_news")
            else:
                context = {"form": form}
                return render(request, "authentication/login.html",context)
        else:
            context = {"form": form}
            return render(request, "authentication/login.html",context)
    else:
        context = {"form": LoginForm()}
        return render(request, "authentication/login.html",context)

@login_required
def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("main_page")