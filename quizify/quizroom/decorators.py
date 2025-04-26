from .models import *
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
def ishost(func):
    def wrapper(request,room_id):
        try:
            room=get_object_or_404(QuizRoom,quiz_id=room_id)
        except:
            return HttpResponse("this room does not exist")
        if room.host==request.user:
            return func(request,room_id)
        else:
            return HttpResponse("unauthorized response")
    return wrapper
        