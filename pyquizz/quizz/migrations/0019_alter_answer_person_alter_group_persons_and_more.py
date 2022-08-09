# Generated by Django 4.0.5 on 2022-08-09 08:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quizz', '0018_auto_20200222_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='person',
            field=models.ForeignKey(help_text='personne questionnée', on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL, verbose_name='personne questionnée'),
        ),
        migrations.AlterField(
            model_name='group',
            name='persons',
            field=models.ManyToManyField(related_name='pyquizz_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]