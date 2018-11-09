"""pyquizz URL Configuration"""
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path("quiz/", include("quizz.urls")),
    path("gestion/", admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
