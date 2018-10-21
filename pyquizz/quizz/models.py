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


# For large amounts of text, use TextField, default widget is then textarea.
