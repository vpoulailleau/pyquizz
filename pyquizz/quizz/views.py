import random

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from .models import Answer, QuizzSending


class Home(View):
    def get(self, request):
        return HttpResponse('Ça marche !')


class AnswerAQuestion(TemplateView):
    template_name = 'quizz/answer_a_question.html'

    def get_context_data(self, **kwargs):
        # TODO better usage of ORM
        kwargs = super().get_context_data(**kwargs)
        date = kwargs['date']
        quizz_sending = QuizzSending.objects.filter(date=date).first()
        email = kwargs['email']
        answers_from_email = Answer.objects.\
            filter(quizz_sending=quizz_sending).\
            filter(person__email=email)
        quizz = quizz_sending.quizz
        unanswered_questions = []
        print(quizz.questions.all())
        for question in quizz.questions.all():
            if answers_from_email.filter(question=question):
                continue
            unanswered_questions.append(question)

        if unanswered_questions:
            kwargs['finished'] = False
            if quizz.random_question_order:
                question = random.choice(unanswered_questions)
            else:
                question = unanswered_questions[0]
            kwargs['question'] = question
        else:
            kwargs['finished'] = True

        kwargs['quizz_sending'] = quizz_sending
        kwargs['answers_from_email'] = answers_from_email
        kwargs['unanswered_questions'] = unanswered_questions
        return kwargs
