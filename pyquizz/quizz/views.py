import random

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import FormView, View

from .models import Answer, QuizzSending
from .forms import AnswerForm


class Home(View):
    def get(self, request):
        return HttpResponse('Ça marche !')


class AnswerAQuestion(FormView):
    template_name = 'quizz/answer_a_question.html'
    success_url = 'form'
    form_class = AnswerForm

    def get(self, request, *args, **kwargs):
        self.date = kwargs['date']
        self.email = kwargs['email']
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.date = kwargs['date']
        self.email = kwargs['email']
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.add_answer_in_database()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # TODO better usage of ORM
        kwargs = super().get_context_data(**kwargs)
        quizz_sending = QuizzSending.objects.filter(date=self.date).first()
        answers_from_email = Answer.objects.\
            filter(quizz_sending=quizz_sending).\
            filter(person__email=self.email)
        quizz = quizz_sending.quizz
        unanswered_questions = []
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

        kwargs['date_for_url'] = self.date.strftime('%Y-%m-%d--%H-%M')
        kwargs['date'] = self.date
        kwargs['email'] = self.email
        return kwargs
