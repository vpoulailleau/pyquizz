from django.urls import path, register_converter
from quizz.views import Home, AnswerAQuestion


class EmailConverter:
    regex = r'\w+@\w+\.\w+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)


register_converter(EmailConverter, 'email')


urlpatterns = [
    path('<email:email>/', AnswerAQuestion.as_view()),
    path('', Home.as_view(), name='home'),
]
