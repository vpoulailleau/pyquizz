# Generated by Django 2.2.7 on 2020-02-22 11:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0016_auto_20190309_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizzsending',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2100, 1, 1, 0, 0), help_text='date de fin du quizz pour un groupe', verbose_name='date de fin du quizz'),
        ),
    ]
