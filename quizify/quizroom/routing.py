from django.urls import re_path
from . import consumers
websocket_urlpatterns=[
    re_path(r"ws/quizroom/(?P<room_name>\w+)/$",consumers.quiz_consumer.as_asgi())
]