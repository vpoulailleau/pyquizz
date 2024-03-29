import random
from collections import defaultdict, namedtuple
from datetime import datetime
from typing import Dict, List

import qrcode
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.template.defaultfilters import register
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import get_fixed_timezone
from django.views.generic import FormView, TemplateView, View


@register.filter(name="dict_key")
def dict_key(d, k):
    """Returns the given key from a dictionary, or an empty list."""
    return d.get(k, [])


from .forms import AnswerForm, ProfileForm, ReviewForm, UploadZipFileForm, UserForm
from .models import Answer, Question, QuizzSending
from .models import ReviewAnswer as ReviewAnswerModel

FetchedAnswer = namedtuple(
    "FetchedAnswer",
    ["email", "nb_points", "question", "quizz_sending", "chosen_answers"],
)
FetchedQuestion = namedtuple("FetchedQuestion", ["pk", "statement", "possible_answers"])
FetchedPerson = namedtuple("FetchedPerson", ["email"])


class AnswerAQuestion(LoginRequiredMixin, FormView):
    template_name = "quizz/answer_a_question.html"
    form_class = AnswerForm

    def get(self, request, *args, **kwargs):
        self.date = kwargs["date"]
        self.date_for_url = self.date.strftime("%Y-%m-%d--%H-%M")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.date = kwargs["date"]
        self.date_for_url = self.date.strftime("%Y-%m-%d--%H-%M")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.add_answer_in_database()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("form", kwargs={"date": self.date_for_url})

    def get_context_data(self, **kwargs):
        # TODO better usage of ORM
        kwargs = super().get_context_data(**kwargs)

        kwargs["date_for_url"] = self.date_for_url
        kwargs["date"] = self.date
        kwargs["email"] = self.request.user.email
        kwargs["form"] = self.get_form()

        quizz_sending = (
            QuizzSending.objects.filter(date=self.date).select_related("quizz").first()
        )
        if not quizz_sending:
            messages.error(self.request, "Pas de quiz correspondant à cette date")
            kwargs["finished"] = False
            kwargs["nb_questions_left"] = 0
            return kwargs
        answers_from_email = (
            Answer.objects.filter(quizz_sending=quizz_sending)
            .select_related("person")
            .filter(person__email=self.request.user.email)
        )

        quizz = quizz_sending.quizz

        fetched_answers: Dict[int, FetchedAnswer] = {}
        for answer in answers_from_email.all():
            fetched_answers[answer.pk] = FetchedAnswer(
                email=answer.person.email,
                nb_points=answer.nb_points,
                question=answer.question.pk,
                quizz_sending=0,  # not used
                chosen_answers="",  # not used
            )

        fetched_questions: Dict[int, FetchedQuestion] = {}
        for question in quizz.questions.all():
            fetched_questions[question.pk] = FetchedQuestion(
                pk=question.pk,
                statement=question.statement_html,
                possible_answers="\n".join(question.possible_answers_html),
            )

        unanswered_questions: List[FetchedQuestion] = []
        for question in fetched_questions.values():
            if any(
                answer.question == question.pk for answer in fetched_answers.values()
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


def user2name(email):
    user = User.objects.filter(email=email).first()
    if user.first_name and user.last_name:
        return f"{user.last_name.upper()} {user.first_name.title()}"
    return f"{user.username.upper()} {user.email}"


class QuizzStatistics(TemplateView):
    template_name = "quizz/statistics.html"

    def generate_qrcode(self, date):
        date_str = str(date).replace(":", "-").replace(" ", "--")
        date_str = date_str[:-3]  # remove seconds, ugly isn't it?
        url = self.request.build_absolute_uri(reverse("form", args=[date_str]))
        qrcode_url = f"qrcodes/{date_str}.png"
        fss = FileSystemStorage()
        filepath = fss.path(qrcode_url)
        if not fss.exists(filepath):
            img = qrcode.make(url, error_correction=qrcode.constants.ERROR_CORRECT_H)
            img.save(filepath)
        return fss.url(qrcode_url)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["qrcode"] = self.generate_qrcode(date=kwargs["date"])
        quizz_sending: QuizzSending = (
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
            messages.error(self.request, "Pas de quizz correspondant à cette date")
            kwargs["quizz_sending"] = None
            return kwargs
        quizz = quizz_sending.quizz
        group = quizz_sending.group

        fetched_questions: Dict[int, FetchedQuestion] = {}
        for question in quizz.questions.all():
            fetched_questions[question.pk] = FetchedQuestion(
                pk=question.pk,
                statement=question.statement_html,
                possible_answers="\n".join(question.possible_answers_html),
            )
        fetched_persons: Dict[str, FetchedPerson] = {}
        for person in group.persons.all():
            fetched_persons[person.email] = FetchedPerson(email=person.email)
        fetched_answers: Dict[int, FetchedAnswer] = {}
        for answer in quizz_sending.answers.all():
            fetched_answers[answer.pk] = FetchedAnswer(
                email=answer.person.email,
                nb_points=answer.nb_points,
                question=answer.question.pk,
                quizz_sending=0,  # not used
                chosen_answers=answer.answers,
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
                    text=user2name(email),
                    value=nb_answers_per_student.get(email, 0),
                    max_value=nb_questions,
                )
            )
        persons_answered_questions.sort(key=lambda p: (p.progress.value, p.text))
        kwargs["persons_answered_questions"] = persons_answered_questions

        persons_correct_questions = []
        for email in fetched_persons:
            answers = (
                answer for answer in fetched_answers.values() if answer.email == email
            )
            nb_points = sum(answer.nb_points for answer in answers)
            persons_correct_questions.append(
                Statistics(
                    text=user2name(email), value=nb_points, max_value=nb_questions
                )
            )
        persons_correct_questions.sort(key=lambda p: p.text)
        kwargs["persons_correct_questions"] = persons_correct_questions

        questions_status = []
        questions_answers_stats = {}
        for question in fetched_questions.values():
            answers = [
                answer
                for answer in fetched_answers.values()
                if answer.question == question.pk
            ]
            nb_points = sum(answer.nb_points for answer in answers)
            questions_status.append(
                Statistics(
                    text=question.statement,
                    value=nb_points,
                    max_value=nb_persons,
                    extra_text=question.possible_answers,
                )
            )
            questions_answers_stats[question.statement] = []
            nb_answers = len(answers)
            for index, possible_answer in enumerate(
                question.possible_answers.splitlines()
            ):
                questions_answers_stats[question.statement].append(
                    Statistics(
                        text=possible_answer,
                        value=sum(
                            1
                            for answer in answers
                            if str(index) in answer.chosen_answers
                        ),
                        max_value=nb_answers,
                    )
                )
        kwargs["questions"] = questions_status
        if datetime.now(tz=get_fixed_timezone(1)) > quizz_sending.end_date:
            kwargs["questions_answers_stats"] = questions_answers_stats
        else:
            kwargs["questions_answers_stats"] = {}

        return kwargs


class QuizzStatisticsCSV(TemplateView):
    template_name = "quizz/statistics.csv"

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
            messages.error(self.request, "Pas de quizz correspondant à cette date")
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

        persons_correct_questions = []
        for email in fetched_persons:
            answers = (
                answer for answer in fetched_answers.values() if answer.email == email
            )
            nb_points = sum(answer.nb_points for answer in answers)
            persons_correct_questions.append(
                Statistics(
                    text=user2name(email),
                    value=nb_points,
                    max_value=nb_questions,
                )
            )
        persons_correct_questions.sort(key=lambda p: p.text)
        kwargs["persons_correct_questions"] = persons_correct_questions
        return kwargs


class StudentStatistics(LoginRequiredMixin, TemplateView):
    template_name = "quizz/student_statistics.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        person = self.request.user

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
            if answer.quizz_sending.started:
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
                if datetime.now(tz=get_fixed_timezone(1)) > quizz_sending.end_date:
                    answers_text = "\n".join(
                        answer.chosen_answers for answer in answers
                    )
                else:
                    answers_text = ""
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
        kwargs["quizzes"] = quizz_sendings_status
        return kwargs


class HelpView(TemplateView):
    template_name = "quizz/help.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            groups = self.request.user.pyquizz_groups.all()
            urls = []
            for group in groups:
                latest_quizz_sending = QuizzSending.objects.filter(group=group).latest(
                    "date"
                )
                urls.append(
                    (
                        latest_quizz_sending.get_absolute_url(),
                        latest_quizz_sending.quizz.name,
                    )
                )
            kwargs["quizzes"] = urls
        else:
            kwargs["quizzes"] = []
        return kwargs


class QuizzStatisticsList(TemplateView):
    template_name = "quizz/quizz_statistics_list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        quizz_sendings = QuizzSending.objects.order_by("-date").select_related(
            "quizz", "group"
        )
        sendings = defaultdict(list)
        for quizz_sending in sorted(
            quizz_sendings, key=lambda qs: (qs.group.name, qs.date.isoformat())
        ):
            sendings[quizz_sending.group.name].append(quizz_sending)
        kwargs["quizz_sendings"] = sendings
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
        kwargs["answers"] = ReviewAnswerModel.objects.filter(review=self.review)
        return kwargs


class UpdateProfile(LoginRequiredMixin, View):
    template_name = "quizz/user_update.html"

    def get_context_data(self, **kwargs):
        if "user_form" not in kwargs:
            kwargs["user_form"] = UserForm(instance=self.request.user)
        if "profile_form" not in kwargs:
            kwargs["profile_form"] = ProfileForm(instance=self.request.user.profile)
        return kwargs

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ctxt = {}
        print(request.POST)

        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid():
            user_form.save()
        if profile_form.is_valid():
            profile_form.save()

        ctxt["user_form"] = user_form
        ctxt["profile_form"] = profile_form

        return render(request, self.template_name, self.get_context_data(**ctxt))


class UploadFile(LoginRequiredMixin, FormView):
    form_class = UploadZipFileForm
    template_name = "quizz/file_upload.html"
    success_url = "/"

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            file = request.FILES["file"]
            user = self.request.user
            filename = f"{kwargs['category']}/{slugify(user.last_name)}_{slugify(user.first_name)}___{slugify(user.username)}.zip"
            fss = FileSystemStorage()
            if fss.exists(filename):
                messages.info(
                    self.request,
                    "Le fichier déjà existant a été supprimé, le nouveau fichier va l'écraser.",
                )
                fss.delete(filename)
            fss.save(filename, file)
            messages.success(self.request, "Fichier envoyé avec succès !")
            return self.form_valid(form)
        return self.form_invalid(form)
