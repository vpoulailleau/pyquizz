import random
from collections import namedtuple

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .forms import AnswerForm, ReviewForm
from .models import Answer, Person, Question, QuizzSending
from .models import ReviewAnswer as ReviewAnswerModel

FetchedAnswer = namedtuple(
    "FetchedAnswer",
    ["email", "nb_points", "question", "quizz_sending", "chosen_answers"],
)
FetchedQuestion = namedtuple(
    "FetchedQuestion", ["pk", "statement", "possible_answers"]
)
FetchedPerson = namedtuple("FetchedPerson", ["email"])


class AnswerAQuestion(FormView):
    template_name = "quizz/answer_a_question.html"
    form_class = AnswerForm

    def get(self, request, *args, **kwargs):
        self.date = kwargs["date"]
        self.date_for_url = self.date.strftime("%Y-%m-%d--%H-%M")
        self.email = kwargs["email"]
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.date = kwargs["date"]
        self.date_for_url = self.date.strftime("%Y-%m-%d--%H-%M")
        self.email = kwargs["email"]
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.add_answer_in_database()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            "form", kwargs={"email": self.email, "date": self.date_for_url}
        )

    def get_context_data(self, **kwargs):
        # TODO better usage of ORM
        kwargs = super().get_context_data(**kwargs)

        kwargs["date_for_url"] = self.date_for_url
        kwargs["date"] = self.date
        kwargs["email"] = self.email
        kwargs["form"] = self.get_form()

        quizz_sending = (
            QuizzSending.objects.filter(date=self.date)
            .select_related("quizz")
            .first()
        )
        if not quizz_sending:
            messages.error(
                self.request, "Pas de quiz correspondant à cette date"
            )
            kwargs["finished"] = False
            kwargs["nb_questions_left"] = 0
            return kwargs
        answers_from_email = (
            Answer.objects.filter(quizz_sending=quizz_sending)
            .select_related("person")
            .filter(person__email=self.email)
        )

        quizz = quizz_sending.quizz

        fetched_answers = {}
        for answer in answers_from_email.all():
            fetched_answers[answer.pk] = FetchedAnswer(
                email=answer.person.email,
                nb_points=answer.nb_points,
                question=answer.question.pk,
                quizz_sending=0,  # not used
                chosen_answers="",  # not used
            )

        fetched_questions = {}
        for question in quizz.questions.all():
            fetched_questions[question.pk] = FetchedQuestion(
                pk=question.pk,
                statement=question.statement_html,
                possible_answers="\n".join(question.possible_answers_html),
            )

        unanswered_questions = []
        for question in fetched_questions.values():
            if any(
                answer.question == question.pk
                for answer in fetched_answers.values()
            ):
                continue
            unanswered_questions.append(question)

        if unanswered_questions:
            kwargs["finished"] = False
            if quizz.random_question_order:
                question = random.choice(unanswered_questions)
            else:
                question = unanswered_questions[0]
            kwargs["question"] = Question.objects.get(pk=question.pk)
        else:
            kwargs["finished"] = True

        kwargs["quizz_sending"] = quizz_sending
        kwargs["nb_questions_left"] = len(unanswered_questions)
        return kwargs


class Progress:
    def __init__(self, value, max_value):
        self.value = value
        self.max_value = max_value

    @property
    def percentage(self):
        return int(100 * self.value / self.max_value)

    @property
    def note(self):
        return self.percentage / 5

    @property
    def reverse_percentage(self):
        return 100 - self.percentage


class Statistics:
    def __init__(self, text, value, max_value, extra_text=""):
        self.text = text
        self.extra_text = extra_text
        self.progress = Progress(value, max_value)


class QuizzStatistics(TemplateView):
    template_name = "quizz/statistics.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        quizz_sending = (
            QuizzSending.objects.filter(date=kwargs["date"])
            .select_related("quizz")
            .select_related("group")
            .prefetch_related("quizz__questions")
            .prefetch_related("group__persons")
            .prefetch_related("answers")
            .prefetch_related("answers__person")
            .prefetch_related("answers__question")
            .first()
        )
        if not quizz_sending:
            messages.error(
                self.request, "Pas de quizz correspondant à cette date"
            )
            kwargs["quizz_sending"] = None
            return kwargs
        quizz = quizz_sending.quizz
        group = quizz_sending.group

        fetched_questions = {}
        for question in quizz.questions.all():
            fetched_questions[question.pk] = FetchedQuestion(
                pk=question.pk,
                statement=question.statement_html,
                possible_answers="\n".join(question.possible_answers_html),
            )
        fetched_persons = {}
        for person in group.persons.all():
            fetched_persons[person.email] = FetchedPerson(email=person.email)
        fetched_answers = {}
        for answer in quizz_sending.answers.all():
            fetched_answers[answer.pk] = FetchedAnswer(
                email=answer.person.email,
                nb_points=answer.nb_points,
                question=answer.question.pk,
                quizz_sending=0,  # not used
                chosen_answers="",  # not used
            )

        nb_questions = quizz.nb_questions
        nb_persons = quizz_sending.nb_persons
        kwargs["quizz_sending"] = quizz_sending
        kwargs["total_questions"] = Progress(
            value=len(fetched_answers), max_value=nb_questions * nb_persons
        )

        nb_answers_per_student = {}
        for answer in fetched_answers.values():
            nb_answers_per_student[answer.email] = (
                nb_answers_per_student.get(answer.email, 0) + 1
            )

        persons_answered_questions = []
        for email in fetched_persons:
            persons_answered_questions.append(
                Statistics(
                    text=email,
                    value=nb_answers_per_student.get(email, 0),
                    max_value=nb_questions,
                )
            )
        persons_answered_questions.sort(key=lambda p: p.progress.value)
        kwargs["persons_answered_questions"] = persons_answered_questions

        persons_correct_questions = []
        for email in fetched_persons:
            answers = (
                answer
                for answer in fetched_answers.values()
                if answer.email == email
            )
            nb_points = sum(answer.nb_points for answer in answers)
            persons_correct_questions.append(
                Statistics(text=email, value=nb_points, max_value=nb_questions)
            )
        persons_correct_questions.sort(key=lambda p: p.text)
        kwargs["persons_correct_questions"] = persons_correct_questions

        questions_status = []
        for question in fetched_questions.values():
            answers = (
                answer
                for answer in fetched_answers.values()
                if answer.question == question.pk
            )
            nb_points = sum(answer.nb_points for answer in answers)
            questions_status.append(
                Statistics(
                    text=question.statement,
                    value=nb_points,
                    max_value=nb_persons,
                    extra_text=question.possible_answers,
                )
            )
        kwargs["questions"] = questions_status

        return kwargs


class QuizzStatisticsCSV(TemplateView):
    template_name = "quizz/statistics.csv"

    @staticmethod
    def is_ynov_group(group):
        for person in group.persons.all():
            if not person.email.endswith("@ynov.com"):
                return False
        return True

    @staticmethod
    def ynovmail2name(ynov: bool, email):
        if ynov:
            name = email.split("@")[0]
            first_name, last_name = name.split(".")
            return f"{last_name} {first_name}"
        return email

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        quizz_sending = (
            QuizzSending.objects.filter(date=kwargs["date"])
            .select_related("quizz")
            .select_related("group")
            .prefetch_related("quizz__questions")
            .prefetch_related("group__persons")
            .prefetch_related("answers")
            .prefetch_related("answers__person")
            .prefetch_related("answers__question")
            .first()
        )
        if not quizz_sending:
            messages.error(
                self.request, "Pas de quizz correspondant à cette date"
            )
            kwargs["quizz_sending"] = None
            return kwargs
        quizz = quizz_sending.quizz
        group = quizz_sending.group

        fetched_persons = {}
        for person in group.persons.all():
            fetched_persons[person.email] = FetchedPerson(email=person.email)
        fetched_answers = {}
        for answer in quizz_sending.answers.all():
            fetched_answers[answer.pk] = FetchedAnswer(
                email=answer.person.email,
                nb_points=answer.nb_points,
                question=answer.question.pk,
                quizz_sending=0,  # not used
                chosen_answers="",  # not used
            )

        nb_questions = quizz.nb_questions
        kwargs["nb_questions"] = nb_questions
        len(fetched_persons)
        kwargs["quizz_sending"] = quizz_sending

        ynov_group = self.is_ynov_group(group)
        persons_correct_questions = []
        for email in fetched_persons:
            answers = (
                answer
                for answer in fetched_answers.values()
                if answer.email == email
            )
            nb_points = sum(answer.nb_points for answer in answers)
            persons_correct_questions.append(
                Statistics(
                    text=self.ynovmail2name(ynov_group, email),
                    value=nb_points,
                    max_value=nb_questions,
                )
            )
        persons_correct_questions.sort(key=lambda p: p.text)
        kwargs["persons_correct_questions"] = persons_correct_questions
        return kwargs


class StudentStatistics(TemplateView):
    template_name = "quizz/student_statistics.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        person = Person.objects.filter(email=kwargs["email"]).first()
        if not person:
            messages.error(self.request, "Cet email est inconnu.")
            return kwargs

        fetched_answers = {}
        quizz_sending_ids = set()
        for answer in (
            Answer.objects.select_related("person")
            .select_related("question")
            .select_related("quizz_sending")
            .filter(person=person)
            .all()
        ):
            if answer.question.pk not in fetched_answers:
                fetched_answers[answer.question.pk] = []
            fetched_answers[answer.question.pk].append(
                FetchedAnswer(
                    email=answer.person.email,
                    nb_points=answer.nb_points,
                    question=answer.question.pk,
                    quizz_sending=answer.quizz_sending.pk,
                    chosen_answers="\n".join(answer.chosen_answers_html),
                )
            )
            quizz_sending_ids.add(answer.quizz_sending.pk)

        quizz_sendings_status = {}
        for quizz_sending_pk in sorted(quizz_sending_ids, reverse=True):
            # TODO merge request of each quizz_sending
            quizz_sending = (
                QuizzSending.objects.select_related("quizz")
                .prefetch_related("quizz__questions")
                .get(pk=quizz_sending_pk)
            )
            quizz_sendings_status[quizz_sending] = []
            total_points = 0
            max_total_points = 0

            for question in quizz_sending.quizz.questions.all():
                answers = [
                    answer
                    for answer in fetched_answers.get(question.pk, [])
                    if answer.quizz_sending == quizz_sending_pk
                ]
                nb_points = sum(answer.nb_points for answer in answers)
                total_points += nb_points
                max_total_points += 1
                answers_text = "\n".join(
                    answer.chosen_answers for answer in answers
                )
                quizz_sendings_status[quizz_sending].append(
                    Statistics(
                        text=question.statement_html,
                        value=nb_points,
                        max_value=1,
                        extra_text=answers_text,
                    )
                )
            quizz_sendings_status[quizz_sending].insert(
                0,
                Statistics(
                    text="Note du quiz",
                    value=total_points,
                    max_value=max_total_points,
                ),
            )
        # TODO quizz_sendings_status.sort(key=lambda q: q.date, reverse=True)
        kwargs["quizzes"] = quizz_sendings_status
        return kwargs


class QuizzStatisticsList(TemplateView):
    template_name = "quizz/quizz_statistics_list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        quizz_sendings = QuizzSending.objects.order_by("-date").select_related(
            "quizz"
        )
        kwargs["quizz_sendings"] = quizz_sendings
        return kwargs


class ReviewAnswer(SuccessMessageMixin, FormView):
    template_name = "quizz/answer_review.html"
    form_class = ReviewForm
    success_message = (
        "Merci pour tes réponses. Tu peux éventuellement en ajouter d'autres."
    )

    def get(self, request, *args, **kwargs):
        self.review = kwargs["review"]
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.review = kwargs["review"]
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["review"] = self.review
        return kwargs

    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.review = self.review
        answer.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("review_answer", kwargs={"review": self.review})


class Review(TemplateView):
    template_name = "quizz/review.html"

    def get(self, request, *args, **kwargs):
        self.review = kwargs["review"]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["review"] = self.review
        kwargs["answers"] = ReviewAnswerModel.objects.filter(
            review=self.review
        )
        return kwargs


class ReviewList(TemplateView):
    pass
