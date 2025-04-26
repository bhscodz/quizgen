from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
app_name="accounts"
urlpatterns = [
    path("login",views.login_user,name="login_user"),
    path("signup",views.signup_user,name="signup_user"),
    path('logout',views.logout_user,name='logout'),
    path('profile',views.profile,name='profile'),
    path('guest', views.guest_login, name='guest_login'),
    path('edit',views.edit_profile,name="edit_profile"),
]
