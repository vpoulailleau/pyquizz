# pyquizz
Website for quizzes (python/Django).

This is a quick and dirty project, just to fulfill my needs. I need to send quizzes to students, get their answers, and make statistics.

# Licence

3-clause BSD

# Design notes

Un groupe est une liste de personnes

Une personne a une adresse mail

Un questionnaire a :

 * une liste de questions
 * ordre aléatoire des questions ou non

Une question a :

 * un énoncé
 * une liste des réponses possibles (un champ texte séparé par des ----)
 * une liste des réponses correctes (un numéro dans la liste des réponses possibles, démarrant à 0, séparé par des virgules)
 * au passage les textes sont en markdown

Il faut qu'une personne puisse répondre plusieurs fois à la même question (genre questionnaire d'autoévaluation).

Un envoi de questionnaire a :

 * une date
 * une référence à un questionnaire
 * une référence à un groupe de personne (pour surveiller que tout le monde a répondu)

Une réponse a :

 * référence à un envoi de questionnaire
 * référence à une personne
 * référence à une question
 * une liste des réponses choisies (un numéro dans la liste des réponses possibles, démarrant à 0)