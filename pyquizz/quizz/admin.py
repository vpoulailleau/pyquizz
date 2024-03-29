from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html, format_html_join

from .models import Answer, Group, Profile, Question, Quizz, QuizzSending, ReviewAnswer


def user_display(user: User) -> str:
    if user.first_name or user.last_name:
        return f"{user.last_name.title()} {user.first_name.title()} ({user.username})"
    return f"({user.username})"


User.__str__ = user_display


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profils"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    ordering = ["last_name", "first_name", "username"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


def format_list(generator):
    return format_html(
        "<ul>\n{}\n</ul>",
        format_html_join("\n", "<li>{}</li>", ((str(item),) for item in generator)),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("persons",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    @admin.display(
        description="quizz"
    )
    def quizzes_display(self, obj):
        return format_list(obj.quizzes.all())


    @admin.display(
        description="réponses"
    )
    def answers_display(self, obj):
        return format_list(obj.correct_answers_text)


    list_display = ("statement", "quizzes_display", "answers_display")
    prepopulated_fields = {"slug": ("statement",)}


@admin.register(Quizz)
class QuizzAdmin(admin.ModelAdmin):
    @admin.display(
        description="questions"
    )
    def questions_display(self, obj):
        return format_list(obj.questions.all())


    list_display = ("name", "random_question_order", "questions_display")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("questions",)


@admin.register(QuizzSending)
class QuizzSendingAdmin(admin.ModelAdmin):
    list_display = ("date", "quizz", "group")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    @admin.display(
        description="quizz"
    )
    def quizz_sending_quizz(self, obj):
        return str(obj.quizz_sending.quizz)


    @admin.display(
        description="réponses"
    )
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


    list_display = (
        "quizz_sending_quizz",
        "person",
        "question",
        "answers_display",
        "quizz_sending",
    )
    search_fields = ("person__email", "quizz_sending__quizz__name")


@admin.register(ReviewAnswer)
class ReviewAnswerAdmin(admin.ModelAdmin):
    search_fields = ("review", "email")
    list_display = ("review", "email")
