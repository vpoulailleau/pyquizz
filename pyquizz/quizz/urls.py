import re
from datetime import datetime

from django.urls import path, register_converter

from quizz.views import AnswerAQuestion, Home


class EmailConverter:
    regex = r'\w+@\w+\.\w+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class DateTimeConverter:
    regex = r'(\d{4})-(\d{2})-(\d{2})--(\d{2})-(\d{2})'

    def to_python(self, value):
        m = re.search(self.regex, value)
        year, month, day, hour, minute = (int(v) for v in m.groups())
        return datetime(
            year,
            month,
            day,
            hour,
            minute,
        )

    def to_url(self, value):
        return value


register_converter(EmailConverter, 'email')
register_converter(DateTimeConverter, 'date')


urlpatterns = [
    path('<email:email>/<date:date>/', AnswerAQuestion.as_view()),
    path('', Home.as_view(), name='home'),
]
