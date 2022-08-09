from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.timezone import get_fixed_timezone

from .models import Answer, Profile, Question, QuizzSending, ReviewAnswer


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

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email):
            raise forms.ValidationError("Cet email est inconnu.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if "quizz_sending" not in cleaned_data:
            raise forms.ValidationError("Ce quizz n'existe pas. Vérifiez la date.")
        if "email" not in cleaned_data:
            raise forms.ValidationError("Cet email est inconnu.")
        quizz_sending = QuizzSending.objects.get(pk=cleaned_data["quizz_sending"])
        if not quizz_sending.group.persons.filter(email=cleaned_data["email"]):
            raise forms.ValidationError("Ce quizz n'est pas fait pour vous.")
        if not any(
            (
                self.cleaned_data["answer0"],
                self.cleaned_data["answer1"],
                self.cleaned_data["answer2"],
                self.cleaned_data["answer3"],
                self.cleaned_data["answer4"],
                self.cleaned_data["answer5"],
                self.cleaned_data["answer6"],
                self.cleaned_data["answer7"],
                self.cleaned_data["answer8"],
                self.cleaned_data["answer9"],
            )
        ):
            raise forms.ValidationError("Aucune réponse n'a été fournie.")
        already_given_answers = (
            Answer.objects.filter(quizz_sending=quizz_sending)
            .filter(person=User.objects.get(email=self.cleaned_data["email"]))
            .filter(question=Question.objects.get(pk=self.cleaned_data["question"]))
        )
        if already_given_answers:
            raise forms.ValidationError(
                "Une réponse a déjà été fournie à la question précédente."
            )

        if datetime.now(tz=get_fixed_timezone(1)) > quizz_sending.end_date:
            raise forms.ValidationError("Ce quiz est maintenant terminé")

    def add_answer_in_database(self):
        quizz_sending = QuizzSending.objects.get(pk=self.cleaned_data["quizz_sending"])
        person = User.objects.get(email=self.cleaned_data["email"])
        question = Question.objects.get(pk=self.cleaned_data["question"])

        answers = []
        for index in range(10):
            answer = self.cleaned_data[f"answer{index}"]
            if answer:
                answers.append(index)
        answers = ",".join(str(answer) for answer in answers)

        answer = Answer(
            quizz_sending=quizz_sending,
            person=person,
            question=question,
            answers=answers,
        )
        answer.save()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewAnswer
        exclude = ["review"]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    error_css_class = "is-invalid"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("dyslexic",)

    error_css_class = "is-invalid"


class UploadZipFileForm(forms.Form):
    file = forms.FileField(
        max_length=1024,
        allow_empty_file=False,
        validators=[
            FileExtensionValidator(allowed_extensions=["zip", "tar.gz", "tgz"]),
        ],
    )

    def clean_file(self):
        data = self.cleaned_data["file"]
        if data.size > 2 * 1024 * 1024:
            raise ValidationError("File too large. Size should not exceed 2 MiB.")
        if data.content_type not in ("application/zip", "application/gzip"):
            raise ValidationError("Invalid content type")
        return data
