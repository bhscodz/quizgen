from django.urls import path
from . import views
app_name="quizroom"
urlpatterns = [
    path("",views.connect_to_server,name="connect_to_server"),
    path("manage/<str:room_id>",views.manage,name="manage"),
]
