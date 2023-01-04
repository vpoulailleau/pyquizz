import re
from datetime import datetime

from django.urls import path, register_converter

from quizz.views import (
    AnswerAQuestion,
    HelpView,
    QuizzStatistics,
    QuizzStatisticsCSV,
    QuizzStatisticsList,
    Review,
    ReviewAnswer,
    StudentStatistics,
    UpdateProfile,
    UploadFile,
)


class EmailConverter:
    regex = r"[\w.-]+@[\w.-]+\.\w+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class DateTimeConverter:
    regex = r"(\d{4})-(\d{2})-(\d{2})--(\d{2})-(\d{2})"

    def to_python(self, value):
        m = re.search(self.regex, value)
        year, month, day, hour, minute = (int(v) for v in m.groups())
        return datetime(year, month, day, hour, minute)

    def to_url(self, value):
        return value


def review_list():
    """Generate regex for reviews.

    For instance B1a-2022.
    """
    current_year = datetime.now().date().year
    reviews = [
        "B1a",
        "B1b",
        "B1c",
        "BTS-SN-1",
        "BTS-SN-2",
        "B3R",
        "B3I",
        "M1M2",
        "piscine",
        "arinfo",
    ]
    dated_reviews = []
    for review in reviews:
        review = review.replace("-", r"\-")
        dated_reviews.append(f"(?:{review}\\-{current_year})")
        dated_reviews.append(f"(?:{review}\\-{current_year - 1})")
    return "|".join(dated_reviews)


class ReviewConverter:
    """URL converter for review."""

    regex = review_list()

    def to_python(self, value):
        """Convert URL element to python value."""
        return value

    def to_url(self, value):
        """Convert python value to URL element."""
        return value


register_converter(EmailConverter, "email")
register_converter(DateTimeConverter, "date")
register_converter(ReviewConverter, "review_type")


urlpatterns = [
    path(
        "review/<review_type:review>/",
        ReviewAnswer.as_view(),
        name="review_form",
    ),
    path(
        "review/<review_type:review>/answers/",
        Review.as_view(),
        name="review_answer",
    ),
    path("<date:date>/", AnswerAQuestion.as_view(), name="form"),
    path(
        "statistiques/<date:date>/csv",
        QuizzStatisticsCSV.as_view(content_type="text/plain"),
        name="quizz_statistics_csv",
    ),
    path(
        "statistiques/<date:date>/", QuizzStatistics.as_view(), name="quizz_statistics"
    ),
    path(
        "statistiques/",
        QuizzStatisticsList.as_view(),
        name="quizz_statistics_list",
    ),
    path("aide/", HelpView.as_view(), name="quizz_help"),
    path("profil/", UpdateProfile.as_view(), name="update_profile"),
    path("upload/<slug:category>/", UploadFile.as_view(), name="upload"),
    path("", StudentStatistics.as_view(), name="student_statistics"),
]
