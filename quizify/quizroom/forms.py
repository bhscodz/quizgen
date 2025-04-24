from django.forms.models import ModelForm
from models import Question
class question_creation_form(ModelForm):
    class Meta:
        model=Question
        fields=["*"]
