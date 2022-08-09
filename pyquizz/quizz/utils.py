from django.utils.text import slugify
from quizz.models import Question, Quizz

# def init_group(name, emails):
#     """
#     Create a group from an email list in a string

#     "toto@toto.com, titi@titi.com, tutu@tutu.com"
#     """
#     slug = slugify(name)[:50]
#     try:
#         group = Group.objects.get(slug=slug)
#     except Group.DoesNotExist:
#         group = Group(name=name, slug=slug)
#         group.save()

#     emails = emails.split(", ")

#     persons = []
#     for email in emails:
#         try:
#             person = User.objects.get(email=email)
#         except User.DoesNotExist:
#             person = User(email=email)
#             person.save()
#         persons.append(person)

#     group.persons.add(*persons)


def create_quizz(quizz_name):
    slug = slugify(quizz_name)[:150]
    try:
        quizz = Quizz.objects.get(slug=slug)
    except Quizz.DoesNotExist:
        quizz = Quizz(name=quizz_name, slug=slug, random_question_order=True)
        quizz.save()
    return quizz


def create_question(quizz, question, answers, good_answers):
    slug = slugify(question)[:256]
    try:
        question = Question.objects.get(slug=slug)
    except Question.DoesNotExist:
        question = Question(statement=question, slug=slug)
    question.answers = "----\n".join(answers)
    question.correct_answers = ",".join(str(a) for a in good_answers)
    question.auto_evaluation = False
    question.save()
    quizz.questions.add(question)


def create_autoevaluation(quizz_name, questions):
    quizz = create_quizz(quizz_name)
    quizz.random_question_order = False

    question_list = []
    for question in questions:
        slug = slugify(question)[:256]
        try:
            question = Question.objects.get(slug=slug)
        except Question.DoesNotExist:
            question = Question(statement=question, slug=slug)
        question.answers = (
            "Non acquis\n----\n"
            "En cours d'acquisition\n----\n"
            "Acquis\n----\n"
            "Dépassé"
        )
        question.correct_answers = "3"
        question.auto_evaluation = True
        question.save()
        question_list.append(question)

    quizz.questions.add(*question_list)
    quizz.save()
