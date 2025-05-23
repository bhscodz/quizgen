from django.forms import inlineformset_factory,formset_factory
from quizroom.models import Question,QuizRoom
from django.forms import ModelForm

question_formset=inlineformset_factory(
    QuizRoom,
    Question,
    fileds=["__all__"],
    extra=1,
    can_delete=True
)