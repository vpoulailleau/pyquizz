from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import Answer, Group, Person, Question, Quizz, QuizzSending


def format_list(generator):
    return format_html(
        "<ul>\n{}\n</ul>",
        format_html_join(
            "\n", "<li>{}</li>", ((str(item),) for item in generator)
        ),
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    def groups_display(self, obj):
        return format_list(obj.groups.all())

    groups_display.short_description = "Groupes"

    list_display = ("email", "groups_display")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("persons",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    def quizzes_display(self, obj):
        return format_list(obj.quizzes.all())

    quizzes_display.short_description = "quizz"

    def answers_display(self, obj):
        return format_list(obj.correct_answers_text)

    answers_display.short_description = "réponses"

    list_display = ("statement", "quizzes_display", "answers_display")
    prepopulated_fields = {"slug": ("statement",)}


@admin.register(Quizz)
class QuizzAdmin(admin.ModelAdmin):
    def questions_display(self, obj):
        return format_list(obj.questions.all())

    questions_display.short_description = "questions"

    list_display = ("name", "random_question_order", "questions_display")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("questions",)


@admin.register(QuizzSending)
class QuizzSendingAdmin(admin.ModelAdmin):
    list_display = ("date", "quizz", "group")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    def quizz_sending_quizz(self, obj):
        return str(obj.quizz_sending.quizz)

    quizz_sending_quizz.short_description = "quizz"

    def answers_display(self, obj):
        possible_answers = obj.question.possible_answers
        chosen_answers = obj.chosen_answers
        answers = []
        for chosen_answer in chosen_answers:
            try:
                answers.append(possible_answers[int(chosen_answer)])
            except (IndexError, ValueError):
                answers.append("Réponse invalide")
        return format_list(answers)

    answers_display.short_description = "réponses"

    list_display = (
        "quizz_sending_quizz",
        "person",
        "question",
        "answers_display",
        "quizz_sending",
    )
    search_fields = ("person__email", "quizz_sending__quizz__name")
