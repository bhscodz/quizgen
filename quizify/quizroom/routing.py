from django.urls import re_path
from . import consumers
websocket_urlpatterns=[
    re_path(r"ws/quizroom/",consumers.quiz_consumer.as_asgi()),
    re_path(r"ws/quizroom/waiting_room/",consumers.waiting_for_host.as_asgi()),
]