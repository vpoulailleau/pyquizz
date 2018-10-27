"""pyquizz URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('quizz/', include('quizz.urls')),
    path('gestion/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
