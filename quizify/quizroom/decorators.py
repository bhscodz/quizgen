from .models import *
from django.shortcuts import HttpResponse
def ishost(func):
    def wrapper(request,room_id):
        room=QuizRoom.objects.filter(quiz_id=room_id)
        if room:
            if room[0].host==request.user:
                return func(request,room_id)
            else:
                return HttpResponse("unothorized request")
        else:
            return HttpResponse("this room doesnt exist anymore")
    return wrapper