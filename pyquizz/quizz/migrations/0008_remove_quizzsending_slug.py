# Generated by Django 2.1.2 on 2018-10-21 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0007_quizzsending_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizzsending',
            name='slug',
        ),
    ]