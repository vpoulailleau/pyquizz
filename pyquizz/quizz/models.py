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


# For large amounts of text, use TextField, default widget is then textarea.
