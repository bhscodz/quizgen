from django.shortcuts import render
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from .models import *
# Create your views here.
def connect_to_server(request):
    if request.method=="POST":
        room_code=request.POST.get("room_code")
        user_name=request.POST.get("username")
        room=get_object_or_404(QuizRoom,quiz_id=room_code)
        request.session["verified"]=True
        session_id=request.session["session_key"]
        if not cache.get(f"participant:{session_id}"):
            cache.set(f"participant:{session_id}",{
                "username":user_name,
                "quiz_id":"room_code",
                "score":0,
                "answers":{},
                "current_que":None,
                "started":False
            })
        return render(request,"quizroom.html",{"username":user_name})
    else:
        data=cache.get(f"participant:{request.session["session_key"]}",None)
        if data:
            return render(request,"quizroom.html",{"username":data["username"]})
        else:
            return render(request,"verify.html")