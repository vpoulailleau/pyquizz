from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView


class Home(View):
    def get(self, request):
        return HttpResponse('Ça marche !')


class AnswerAQuestion(TemplateView):
    template_name = 'quizz/answer_a_question.html'
