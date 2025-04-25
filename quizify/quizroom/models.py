from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class QuizRoom(models.Model):
    quiz_name=models.CharField(blank=False,unique=True,max_length=100)
    quiz_id = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_quizzes')
    number_of_questions = models.PositiveIntegerField(editable=False,default=0) #editable=False
    date_created = models.DateTimeField(auto_now_add=True)
    choices=[("NS","not started"),
             ("OG","on going"),
             ("EN",'ended'),]
    status=models.CharField(choices=choices,max_length=255,default="NS")
    def __str__(self):
        return f"QuizRoom {self.quiz_id} by {self.host.username}"

class Question(models.Model):
    room = models.ForeignKey('QuizRoom', on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_image=models.ImageField(upload_to="question_image",max_length=100,blank=True,null=True)
    duration = models.PositiveIntegerField(default=10)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    
    CORRECT_OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    correct_option = models.CharField(max_length=1, choices=CORRECT_OPTION_CHOICES)
    
    points = models.PositiveIntegerField(default=1)
    def save(self):
        self.room.number_of_questions+=1
        self.room.save()
        return super().save()
    def __str__(self):
        return f"Question in {self.room.quiz_id}: {self.question_text[:50]}"