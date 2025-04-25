from django.forms import inlineformset_factory,formset_factory
from quizroom.models import Question,QuizRoom
from django.forms import ModelForm

class  create_quiz(ModelForm):
    class Meta:
        model=QuizRoom
        fields=["quiz_name","quiz_id"]

question_formset=inlineformset_factory(
    QuizRoom,
    Question,
    exclude=["room","id"],
    extra=1,
    can_delete=True
)

