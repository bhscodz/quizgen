from django.shortcuts import render,redirect
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import ishost
from .models import *
from django.contrib import messages
# Create your views here.
def connect_to_server(request):
    if request.method=="POST":
        room_code=request.POST.get("room_code")
        user_name=request.POST.get("username")
        room=get_object_or_404(QuizRoom,quiz_id=room_code)
        request.session["verified"]=True
        request.session["quizid"]=room.quiz_id
        if not cache.get(f"master:{room.quiz_id}_master_is_on"):
            return render(request,"waiting_page.html")
        session_id=request.session.session_key
        if not cache.get(f"participant:{session_id}"):
            cache.set(f"participant:{session_id}",{
                "username":user_name,
                "quiz_id":"room_code",
                "score":0,
                "answers":{},
                "leader_board":{},
                "started":False
            })
        else:
            request.session["reconnected"]=True
        return render(request,"quizroom.html",{"username":user_name})
    else:
        data=cache.get(f"participant:{request.session.session_key}",None)
        if data:
            request.session["reconnected"]=True
            return render(request,"quizroom.html",{"username":data["username"]})
        else:
            return redirect("home")

@login_required(login_url="accounts:login_user")
@ishost        
def manage(request,room_id):
    room=QuizRoom.objects.get(room_id)
    return render(request,"host_view.html" ,{"room":room})