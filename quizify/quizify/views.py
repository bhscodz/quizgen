from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from quizroom.models import QuizRoom
from django.shortcuts import HttpResponse
from .forms import create_quiz,question_formset
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
def home(request):
    subject_categories = ['Math', 'Science', 'History', 'Programming', 'General Knowledge', 'Sports']
    return render(request,'home.html',{'subject_categories':subject_categories})
def about(request):
    return render(request,'about.html')
@login_required(login_url="accounts:login_user")
def manage_quiz(request):
    all_rooms=QuizRoom.objects.filter(host=request.user)
    return render(request,'manage_quiz.html',{"all_quizes":all_rooms})
def quizzes(request):
    return render (request,"quizzes.html")
def home(request):
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
            return redirect(f"add_question/{room}")
    return render(request,"create_quiz.html",{"form":form})

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
                return redirect("home")
            else:
                print(form.errors)
        return render(request,"add_questions.html",{"form":form})
    else:
        return HttpResponse("room does not exist")