from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import Group, Person, Question, Quizz


def format_list(generator):
    return format_html(
        '<ul>\n{}\n</ul>',
        format_html_join(
            '\n',
            '<li>{}</li>',
            ((str(item),) for item in generator)
        )
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    def groups_display(self, obj):
        return format_list(obj.groups.all())
    groups_display.short_description = 'Groupes'

    list_display = ('email', 'groups_display')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('persons',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    def quizzes_display(self, obj):
        return format_list(obj.quizzes.all())
    quizzes_display.short_description = 'quizz'

    list_display = ('statement', 'quizzes_display')
    prepopulated_fields = {'slug': ('statement',)}


@admin.register(Quizz)
class QuizzAdmin(admin.ModelAdmin):
    def questions_display(self, obj):
        return format_list(obj.questions.all())
    questions_display.short_description = 'questions'

    list_display = ('name', 'random_question_order', 'questions_display')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('questions',)
