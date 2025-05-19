from django import forms
from django.core.exceptions import ValidationError

from .models import Question, Choice

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.question:
            instance.question = self.question
        if commit:
            instance.save()
        return instance


    def clean_choice_text(self):
        choice_text = self.cleaned_data['choice_text']
        question = self.question or getattr(self.instance, 'question', None)
        if not question:
            raise ValidationError("Choice must be associated with a question.")

        if question.choice_set.filter(choice_text=choice_text).exists():
            raise ValidationError("This choice already exists for the question.")
        return choice_text