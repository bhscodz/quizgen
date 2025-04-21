from django.urls import path
from . import views
app_name="accounts"
urlpatterns = [
    path("signup/",views.signup_user,name="signup"),
    path("login",views.login_user,name="login_user"),
    path('logout',views.logout_user,name='logout'),
    path('profile',views.profile,name='profile'),
    path('guest', views.guest_login, name='guest_login'),
]
