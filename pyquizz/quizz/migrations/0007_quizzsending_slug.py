# Generated by Django 2.1.2 on 2018-10-21 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0006_auto_20181021_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizzsending',
            name='slug',
            field=models.SlugField(default='toto', help_text="slug de l'envoi (basé sur la date)", max_length=20, unique=True, verbose_name='slug'),
            preserve_default=False,
        ),
    ]
