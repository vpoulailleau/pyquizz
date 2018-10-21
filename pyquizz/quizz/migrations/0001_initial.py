# Generated by Django 2.1.2 on 2018-10-21 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='nom du groupe', max_length=32, unique=True, verbose_name='nom')),
                ('slug', models.SlugField(help_text='slug du groupe (basé sur le nom)', unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Groupe',
                'verbose_name_plural': 'Groupes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(help_text='email de la personne', max_length=255, unique=True, verbose_name='email')),
            ],
            options={
                'verbose_name': 'Personne',
                'verbose_name_plural': 'Personnes',
                'ordering': ['email'],
            },
        ),
    ]
