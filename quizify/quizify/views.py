from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from quizroom.models import QuizRoom
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