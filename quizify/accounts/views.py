from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
# Create your views here.
def signup_user(request):
    pass
def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("home")  # Change "home" to your actual home view name
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")
def logout_user(request):
    return render(request,'login.html')
def profile(request):
    return render(request,'profile.html')
def guest_login(request):
    guest_username = "Guest"
    user, created = User.objects.get_or_create(username=guest_username)
    if created:
        user.set_unusable_password()
        user.save()
    login(request, user)
    return redirect("home")