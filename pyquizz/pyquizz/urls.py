"""pyquizz URL Configuration"""
from django.conf import settings
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
    path(
        "favicon.ico", RedirectView.as_view(url="/static/pyquizz/favicon.ico")
    ),
    path(
        "apple-touch-icon.png",
        RedirectView.as_view(url="/static/pyquizz/apple-touch-icon.png"),
    ),
    path(
        "apple-touch-icon-precomposed.ico",
        RedirectView.as_view(
            url="/static/pyquizz/apple-touch-icon-precomposed.ico"
        ),
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

urlpatterns += staticfiles_urlpatterns()
