# Generated by Django 2.1.2 on 2019-03-09 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0012_reviewanswer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reviewanswer',
            options={'ordering': ['review', 'email', 'pk'], 'verbose_name': 'Réponse à un bilan', 'verbose_name_plural': 'Réponses à un bilan'},
        ),
    ]
