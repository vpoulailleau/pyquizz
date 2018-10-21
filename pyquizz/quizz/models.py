from django.db import models
from django.urls import reverse


class Person(models.Model):
    email = models.EmailField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='email',
        help_text='email de la personne',
        max_length=255,
    )

    class Meta:
        ordering = ['email']
        verbose_name = 'Personne'
        verbose_name_plural = 'Personnes'

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('quizz_person_detail', args=[str(self.email)])


class Group(models.Model):
    name = models.CharField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='nom',
        help_text='nom du groupe',
        max_length=32,
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='slug',
        help_text='slug du groupe (basé sur le nom)',
        max_length=50,
    )
    persons = models.ManyToManyField(
        Person,
        related_name='groups',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Groupe'
        verbose_name_plural = 'Groupes'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('quizz_group_detail', args=[str(self.slug)])


class Question(models.Model):
    statement = models.TextField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='énoncé',
        help_text='énoncé de la question',
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='slug',
        help_text='slug de la question (basé sur l\'énoncé)',
        max_length=256,
    )
    answers = models.TextField(
        null=False,
        blank=False,
        unique=False,
        verbose_name='réponses',
        help_text='réponses à la question séparées par des ----'
    )
    correct_answers = models.CharField(
        null=False,
        blank=False,
        unique=False,
        verbose_name='réponses correctes',
        help_text=('numéro des réponses correctes à la question '
                   'séparées par des virgules, démarrant à 0'),
        max_length=10,
    )

    class Meta:
        ordering = ['statement']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return self.statement

    def get_absolute_url(self):
        return reverse('quizz_question_detail', args=[str(self.slug)])


class Quizz(models.Model):
    name = models.CharField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='nom',
        help_text='nom du quizz',
        max_length=128,
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='slug',
        help_text='slug du quizz (basé sur le nom)',
        max_length=150,
    )
    questions = models.ManyToManyField(
        Question,
        related_name='quizzes',
    )
    random_question_order = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        verbose_name='ordre aléatoire des questions',
        help_text='est-ce que les questions seront posées en ordre aléatoire',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Quizz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('quizz_quizz_detail', args=[str(self.slug)])


class QuizzSending(models.Model):
    quizz = models.ForeignKey(
        Quizz,
        on_delete=models.CASCADE,
        related_name='quizz_sendings',
        blank=False,
        null=False,
        verbose_name='quizz',
        help_text='quizz à envoyer',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='quizz_sendings',
        blank=False,
        null=False,
        verbose_name='groupe',
        help_text='groupe destinataire du quizz',
    )
    date = models.DateTimeField(
        null=False,
        blank=False,
        unique=True,
        verbose_name="date d'envoi du quizz",
        help_text="date d'envoi du quizz à un groupe"
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Envoi de quizz'
        verbose_name_plural = 'Envois de quizz'

    def __str__(self):
        return f'envoi du {self.date} de {self.quizz} à {self.group}'

    def get_absolute_url(self):
        return reverse('quizz_quizzsending_detail', args=[str(self.date)])
