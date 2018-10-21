from django import forms


class AnswerForm(forms.Form):
    email = forms.CharField(max_length=255)
    question = forms.IntegerField(min_value=0)
    quizz_sending = forms.IntegerField(min_value=0)
    answer0 = forms.BooleanField(required=False)
    answer1 = forms.BooleanField(required=False)
    answer2 = forms.BooleanField(required=False)
    answer3 = forms.BooleanField(required=False)
    answer4 = forms.BooleanField(required=False)
    answer5 = forms.BooleanField(required=False)
    answer6 = forms.BooleanField(required=False)
    answer7 = forms.BooleanField(required=False)
    answer8 = forms.BooleanField(required=False)
    answer9 = forms.BooleanField(required=False)
