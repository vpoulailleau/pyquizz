from django.urls import path
from quizz import views

urlpatterns = [
    path("", views.home, name="home"),
]
