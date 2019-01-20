"""pyquizz URL Configuration"""
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("quiz/", include("quizz.urls")),
    path("gestion/", admin.site.urls),
    path(
        "favicon.png", RedirectView.as_view(url="/static/pyquizz/favicon.png")
    ),
]

urlpatterns += staticfiles_urlpatterns()
