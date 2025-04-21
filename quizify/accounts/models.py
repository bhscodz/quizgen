from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class User_data(models.Model):
    user=models.ForeignKey(User, related_name="profile_data", on_delete=models.CASCADE)
    total_quizzes_played = models.PositiveIntegerField(default=0)
    total_points_earned = models.PositiveIntegerField(default=0)
    avatar=models.ImageField(upload_to="avatar")