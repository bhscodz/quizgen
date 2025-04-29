from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from quizroom.models import QuizRoom
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from .forms import create_quiz,question_formset
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .decorators import ishost
from django.contrib import messages
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
def about(request):
    return render(request,'about.html')
@login_required(login_url="accounts:login_user")
def manage_quiz(request):
    all_rooms=QuizRoom.objects.filter(host=request.user)
    return render(request,'manage_quiz.html',{"all_quizes":all_rooms})
def quizzes(request):
    return render (request,"quizzes.html")
def home(request):
    messages.success(request, f"Welcome {request.user}")
    return render(request,"home.html")
def join_quiz(request):
    #logic to travel to the quiz page according to input code
    return render(request,'quizzes.html')
@login_required(login_url="accounts:login_user")
def create_quiz_room(request):
    form=create_quiz()
    if request.method=="POST":
        form=create_quiz(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            room=form.quiz_id
            form.host=request.user
            form.save()
            print("saved")
            return redirect(f"add_questions/{room}")
    return render(request,"create_quiz.html",{"form":form,"title":"create"})

@login_required(login_url="accounts:login_user")
def add_questions(request,room_id):
    room=QuizRoom.objects.filter(quiz_id=room_id)
    if request.user!=room[0].host:
        return HttpResponse("you are not allowed to do so, only host can add questions")
    if room:
        room=room[0]
        form=question_formset(instance=room)
        if request.method=="POST":
            form=question_formset(request.POST,request.FILES,instance=room)
            if form.is_valid():
                form.save()
                messages.success(request, f"QUESTIONS ADDED SUCCESSFULLY") 
                return redirect("manage_quiz")
            else:
                print(form.errors)
        return render(request,"add_questions.html",{"form":form})
    else:
        return HttpResponse("room does not exist")

@login_required(login_url="accounts:login_user")
@ishost
def update_room(request,room_id):
    room=QuizRoom.objects.get(quiz_id=room_id)
    form = create_quiz(instance=room)
    if request.method=="POST":
        form=create_quiz(request.POST,instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f"quiz updated successfully") 
            return redirect("manage_quiz")
    return render(request,"create_quiz.html",{"form":form,"title":"update"})

@login_required(login_url="accounts:login_user")
@ishost
def delete_room(request,room_id):
    room=QuizRoom.objects.get(quiz_id=room_id)
    info=room.delete()
    if info[0]:
        return JsonResponse({"success":info})
    else:
        return JsonResponse({"error":"failed to delete room"})
    