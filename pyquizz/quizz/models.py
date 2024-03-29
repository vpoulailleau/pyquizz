import re
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.timezone import get_default_timezone


def md2html(text):
    text = text.replace("<", "&lt;")
    text = text.replace("&lt;sub>", "<sub>").replace("&lt;/sub>", "</sub>")
    text = text.replace("&lt;sup>", "<sup>").replace("&lt;/sup>", "</sup>")
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)
    return mark_safe(text)


class Group(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"

    name = models.CharField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="nom",
        help_text="nom du groupe",
        max_length=32,
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="slug",
        help_text="slug du groupe (basé sur le nom)",
        max_length=50,
    )
    persons = models.ManyToManyField(User, related_name="pyquizz_groups")

    def get_absolute_url(self):
        return reverse("quizz_group_detail", args=[str(self.slug)])

    def __str__(self):
        return self.name


class Question(models.Model):
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    statement = models.TextField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="énoncé",
        help_text="énoncé de la question",
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="slug",
        help_text="slug de la question (basé sur l'énoncé)",
        max_length=256,
    )
    answers = models.TextField(
        null=False,
        blank=False,
        unique=False,
        verbose_name="réponses",
        help_text="réponses à la question séparées par des ----",
    )
    correct_answers = models.CharField(
        null=False,
        blank=False,
        unique=False,
        verbose_name="réponses correctes",
        help_text=(
            "numéro des réponses correctes à la question "
            "séparées par des virgules, démarrant à 0"
        ),
        max_length=20,
    )
    auto_evaluation = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="question d'auto-évaluation",
        help_text="est-ce une question d'auto-évaluation",
    )

    def get_absolute_url(self):
        return reverse("quizz_question_detail", args=[str(self.slug)])

    @cached_property
    def statement_html(self):
        return md2html(self.statement)

    @cached_property
    def possible_answers(self):
        answers = [answer.strip() for answer in str(self.answers).split("----")]
        if not self.auto_evaluation:
            answers.append("Sans opinion")
        return answers

    @cached_property
    def possible_answers_html(self):
        return [md2html(a) for a in self.possible_answers]

    @cached_property
    def correct_answers_text(self):
        correct_answers = [int(num) for num in str(self.correct_answers).split(",")]
        possible_answers = self.possible_answers
        return [possible_answers[i] for i in correct_answers]

    @cached_property
    def correct_answers_html(self):
        return [md2html(a) for a in self.correct_answers_text]

    def nb_points(self, answer):
        if self.auto_evaluation:
            ret = 0
            for chosen in answer.chosen_answers:
                if chosen:
                    ret = min(2, max(int(chosen), ret))
            # consider that the user knows at least the subject
            return ret / 2
        else:
            points = 1.0
            correct_answers = self.correct_answers.split(",")
            answers = answer.answers.split(",")
            for answer in correct_answers:
                if answer not in answers:
                    points -= 0.5
            for answer in answers:
                if answer not in correct_answers:
                    points -= 0.5
            return max(0, points)

    def __str__(self):
        return self.statement


class Quizz(models.Model):
    class Meta:
        ordering = ["slug"]
        verbose_name = "Quizz"
        verbose_name_plural = "Quizzes"

    name = models.CharField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="nom",
        help_text="nom du quizz",
        max_length=128,
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="slug",
        help_text="slug du quizz (basé sur le nom)",
        max_length=150,
    )
    questions = models.ManyToManyField(Question, related_name="quizzes")
    random_question_order = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        verbose_name="ordre aléatoire des questions",
        help_text="est-ce que les questions seront posées en ordre aléatoire",
    )

    def get_absolute_url(self):
        return reverse("quizz_quizz_detail", args=[str(self.slug)])

    @cached_property
    def nb_questions(self):
        return self.questions.count()

    def __str__(self):
        return f"{self.name} ({self.nb_questions} questions, {self.nb_questions / 4} minutes)"


class QuizzSending(models.Model):
    class Meta:
        ordering = ["-date"]
        verbose_name = "Envoi de quizz"
        verbose_name_plural = "Envois de quizz"

    quizz = models.ForeignKey(
        Quizz,
        on_delete=models.CASCADE,
        related_name="quizz_sendings",
        blank=False,
        null=False,
        verbose_name="quizz",
        help_text="quizz à envoyer",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="quizz_sendings",
        blank=False,
        null=False,
        verbose_name="groupe",
        help_text="groupe destinataire du quizz",
    )
    date = models.DateTimeField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="date d'envoi du quizz",
        help_text="date d'envoi du quizz à un groupe",
    )
    end_date = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="date de fin du quizz",
        help_text="date de fin du quizz pour un groupe",
        default=datetime(2100, 1, 1, 0, 0, tzinfo=get_default_timezone()),
    )
    started = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="quiz démarré",
        help_text="est-ce que ce quiz est démarré",
    )

    def get_absolute_url(self):
        return reverse("form", args=[self.date_for_url])

    @cached_property
    def hash(self):
        return hex(abs(hash(self)))

    @cached_property
    def date_for_url(self):
        return self.date.astimezone(get_default_timezone()).strftime("%Y-%m-%d--%H-%M")

    @property
    def nb_persons(self):
        self.answers.all()
        emails = set()
        for p in self.answers.all():
            emails.add(p.person.email)
        return max(1, len(emails))  # avoid division by 0

    def __hash__(self):
        return hash(("QuizzSending", self.date_for_url))

    def __str__(self):
        return f"envoi du {self.date} de {self.quizz} à {self.group}"


class Answer(models.Model):
    class Meta:
        ordering = ["quizz_sending", "person", "question"]
        verbose_name = "Réponse à une question"
        verbose_name_plural = "Réponses à des questions"

    quizz_sending = models.ForeignKey(
        QuizzSending,
        on_delete=models.CASCADE,
        related_name="answers",
        blank=False,
        null=False,
        verbose_name="envoi de quizz",
        help_text="envoi de quizz",
    )
    person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answers",
        blank=False,
        null=False,
        verbose_name="personne questionnée",
        help_text="personne questionnée",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="sent_answers",
        blank=False,
        null=False,
        verbose_name="question",
        help_text="question posée",
    )
    answers = models.CharField(
        null=False,
        blank=False,
        unique=False,
        verbose_name="réponses choisies",
        help_text=(
            "numéro des réponses choisies à la question "
            "séparées par des virgules, démarrant à 0"
        ),
        max_length=20,
    )

    def get_absolute_url(self):
        return reverse("quizz_answer_detail", args=[str(self.pk)])

    @cached_property
    def chosen_answers(self):
        if self.answers:
            return str(self.answers).split(",")
        return []

    @cached_property
    def chosen_answers_textual(self):
        possible_answers = self.question.possible_answers
        return [possible_answers[int(index)] for index in self.chosen_answers]

    @cached_property
    def chosen_answers_html(self):
        possible_answers = self.question.possible_answers
        return [md2html(possible_answers[int(index)]) for index in self.chosen_answers]

    @cached_property
    def nb_points(self):
        return self.question.nb_points(self)

    def __str__(self):
        return (
            f"réponse de {self.person.email} à {self.quizz_sending} "
            f"à la question {self.question} : {self.answers}"
        )


class ReviewAnswer(models.Model):
    class Meta:
        ordering = ["review", "email", "pk"]
        verbose_name = "Réponse à un bilan"
        verbose_name_plural = "Réponses à un bilan"

    review = models.CharField(
        null=False,
        blank=False,
        unique=False,
        verbose_name="Nom du bilan",
        help_text="Nom du bilan, doit pouvoir faire partie d'une URL",
        max_length=20,
    )
    email = models.EmailField(
        null=False,
        blank=True,
        unique=False,  # multiple answers
        verbose_name="Adresse email",
        help_text="Adresse email (facultative)",
    )
    easiest = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le plus facile",
        help_text="Cette année, le plus facile a été",
        max_length=1000,
    )
    hardest = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le plus difficile",
        help_text="Cette année, le plus difficile a été",
        max_length=1000,
    )
    funniest = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le plus amusant",
        help_text="Cette année, le plus amusant a été",
        max_length=1000,
    )
    most_boring = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le plus ennuyant",
        help_text="Cette année, le plus ennuyant a été",
        max_length=1000,
    )
    most_regrettable = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le plus regrettable",
        help_text="Cette année, le plus regrettable a été",
        max_length=1000,
    )
    most_original = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le plus original",
        help_text="Cette année, le plus original a été",
        max_length=1000,
    )
    most_interesting = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le plus intéressant",
        help_text="Cette année, le plus intéressant a été",
        max_length=1000,
    )
    least_interesting = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Le moins intéressant",
        help_text="Cette année, le moins intéressant a été",
        max_length=1000,
    )
    suggestions = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Suggestions d'amélioration",
        help_text="Propositions pour améliorer le cours",
        max_length=1000,
    )
    teacher_appreciation = models.TextField(
        null=False,
        blank=True,
        unique=False,
        verbose_name="Remarques sur le prof",
        help_text="Remarques et appréciations sur le prof",
        max_length=1000,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    dyslexic = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="mode dyslexique",
        help_text="Utilisation d'une police spéciale dyslexique",
    )

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
