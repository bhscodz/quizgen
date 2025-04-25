from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from .forms import create_user
from .decorators import isguest 
# Create your views here.
@isguest
def signup_user(request):
    user_form=create_user()
    if request.method=="POST":
        user_form=create_user(request.POST)
        if user_form.is_valid():
            user_form.save()
            return redirect("accounts:login_user")
        else:
            return render(request,"signup.html",{"form":user_form})
    return render(request,"signup.html",{"form":user_form})
@isguest
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")  # Change "home" to your actual home view name
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

@login_required(login_url="accounts:login_user")
def logout_user(request):
    logout(request)
    return render(request,'login.html')

@login_required(login_url="accounts:login_user")
def profile(request):
    return render(request,'profile.html')

@isguest
def guest_login(request):
    return redirect("home")