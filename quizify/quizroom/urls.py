from django.urls import path
from . import views
urlpatterns = [
    path("",views.connect_to_server,name="connect_to_server")
]
