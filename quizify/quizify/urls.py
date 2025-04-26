"""
URL configuration for quizify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf.urls.static import static
from django.conf import settings
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home,name="home"),
    path('accounts/',include("accounts.urls")),
    path('quizroom/',include("quizroom.urls")),
    path('manage_quiz',views.manage_quiz,name='manage_quiz'),
    path('quizzes',views.quizzes,name='quizzes'),
    path('about',views.about,name='about'),
    path('join_quiz',views.join_quiz,name='join_quiz'),
    path("create_room",views.create_quiz_room,name='create_room'),
    path("update_room/<str:room_id>",views.update_room,name='update_room'),
    path("update_room/<str:room_id>",views.update_room,name='update_room'),
    path("delete_room/<str:room_id>",views.delete_room,name='delete_room'),
    path('add_questions/<str:room_id>',views.add_questions,name='add_questions'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
