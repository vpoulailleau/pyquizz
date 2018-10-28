import random

from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .forms import AnswerForm
from .models import Answer, Person, Question, QuizzSending


class AnswerAQuestion(FormView):
    template_name = 'quizz/answer_a_question.html'
    form_class = AnswerForm

    def get(self, request, *args, **kwargs):
        self.date = kwargs['date']
        self.date_for_url = self.date.strftime('%Y-%m-%d--%H-%M')
        self.email = kwargs['email']
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.date = kwargs['date']
        self.date_for_url = self.date.strftime('%Y-%m-%d--%H-%M')
        self.email = kwargs['email']
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.add_answer_in_database()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(
                self.request,
                error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'form',
            kwargs={
                'email': self.email,
                'date': self.date_for_url})

    def get_context_data(self, **kwargs):
        # TODO better usage of ORM
        kwargs = super().get_context_data(**kwargs)

        kwargs['date_for_url'] = self.date_for_url
        kwargs['date'] = self.date
        kwargs['email'] = self.email
        kwargs['form'] = self.get_form()

        quizz_sending = QuizzSending.objects.filter(date=self.date).first()
        if not quizz_sending:
            messages.error(
                self.request,
                'Pas de quizz correspondant à cette date')
            kwargs['nb_questions_left'] = 0
            return kwargs
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
        kwargs['nb_questions_left'] = len(unanswered_questions)
        return kwargs


class Progress:
    def __init__(self, value, max_value):
        self.value = value
        self.max_value = max_value

    @property
    def percentage(self):
        return 100 * self.value // self.max_value

    @property
    def reverse_percentage(self):
        return 100 - self.percentage


class Statistics:
    def __init__(self, text, value, max_value):
        self.text = text
        self.progress = Progress(value, max_value)


class QuizzStatistics(TemplateView):
    template_name = 'quizz/statistics.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        quizz_sending = QuizzSending.objects.filter(
            date=kwargs['date']).first()
        if not quizz_sending:
            messages.error(
                self.request,
                'Pas de quizz correspondant à cette date')
            kwargs['quizz_sending'] = None
            return kwargs
        quizz = quizz_sending.quizz
        group = quizz_sending.group
        nb_questions = quizz.questions.count()
        nb_persons = group.persons.count()
        kwargs['quizz_sending'] = quizz_sending
        kwargs['total_questions'] = Progress(
            value=Answer.objects.filter(
                quizz_sending=quizz_sending).count(),
            max_value=nb_questions * nb_persons
        )

        persons_answered_questions = []
        for person in group.persons.all():
            persons_answered_questions.append(
                Statistics(
                    text=person.email,
                    value=Answer.objects.filter(
                        quizz_sending=quizz_sending).filter(
                            person__email=person.email).count(),
                    max_value=nb_questions,
                )
            )
        persons_answered_questions.sort(key=lambda p: p.progress.value)
        kwargs['persons_answered_questions'] = persons_answered_questions

        persons_correct_questions = []
        for person in group.persons.all():
            answers = Answer.objects.filter(
                quizz_sending=quizz_sending).filter(
                person__email=person.email).all()
            nb_correct_answers = sum(
                answer.answers == answer.question.correct_answers
                for answer in answers
            )
            persons_correct_questions.append(
                Statistics(
                    text=person.email,
                    value=nb_correct_answers,
                    max_value=nb_questions,
                )
            )
        persons_correct_questions.sort(key=lambda p: p.text)
        kwargs['persons_correct_questions'] = persons_correct_questions

        questions_status = []
        questions = quizz.questions.all()
        for question in questions:
            answers = Answer.objects.filter(
                quizz_sending=quizz_sending).filter(
                question=question).all()
            nb_correct_answers = sum(
                answer.answers == answer.question.correct_answers
                for answer in answers
            )
            questions_status.append(Statistics(
                text=str(question.statement),
                value=nb_correct_answers,
                max_value=nb_persons,
            ))
        kwargs['questions'] = questions_status

        return kwargs


class StudentStatistics(TemplateView):
    template_name = 'quizz/student_statistics.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        person = Person.objects.filter(email=kwargs['email']).first()
        if not person:
            messages.error(self.request, 'Cet email est inconnu.')
            return kwargs
        quizz_sending_id_values = Answer.objects.filter(
            person=person).values('quizz_sending_id').distinct()
        quizz_sendings_status = {}
        for value in quizz_sending_id_values:
            quizz_sending = QuizzSending.objects.get(
                pk=value['quizz_sending_id'])
            quizz_sendings_status[quizz_sending] = []
            for question in quizz_sending.quizz.questions.all():
                answers = Answer.objects.filter(
                    quizz_sending=quizz_sending).filter(
                    question=question).filter(person=person).all()
                nb_correct_answers = sum(
                    answer.answers == answer.question.correct_answers
                    for answer in answers)
                quizz_sendings_status[quizz_sending].append(Statistics(
                    text=str(question.statement),
                    value=nb_correct_answers,
                    max_value=1,
                ))
        # TODO quizz_sendings_status.sort(key=lambda q: q.date, reverse=True)
        kwargs['quizzes'] = quizz_sendings_status
        return kwargs


class QuizzStatisticsList(TemplateView):
    template_name = 'quizz/quizz_statistics_list.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        quizz_sendings = QuizzSending.objects.order_by('-date')
        kwargs['quizz_sendings'] = quizz_sendings
        return kwargs
