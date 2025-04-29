from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from .forms import create_user
from .models import Profile
from .decorators import isguest 
from django.contrib import messages
# Create your views here.
@isguest
def signup_user(request):
    user_form=create_user()
    if request.method=="POST":
        user_form=create_user(request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Profile created please log in")
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
            messages.success(request, f"welcome back {user.username}")
            return redirect("home")  # Change "home" to your actual home view name
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

@login_required(login_url="accounts:login_user")
def logout_user(request):
    logout(request)
    messages.success(request, f"logged out")
    return render(request,'login.html')

@isguest
def guest_login(request):
    messages.success(request, f"welcome guest user")
    return redirect("home")

@login_required(login_url="accounts:login_user")
def profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)  
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile
    })


@login_required(login_url="accounts:login_user")
def edit_profile(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')  # Get uploaded file
        
        # Update User model
        user = request.user
        user.username = username
        user.email = email
        user.save()
        
        # Update Profile model
        profile, created = Profile.objects.get_or_create(user=user)
        profile.bio = bio
        if avatar:  # Only update if new avatar was uploaded
            profile.avatar = avatar
        profile.save()
        messages.success((request),"Your profile has been updated .")
        
        return redirect('accounts:profile')  # Redirect to profile page after saving
    
    return render(request, 'edit_profile.html', {
        'user': request.user
    })