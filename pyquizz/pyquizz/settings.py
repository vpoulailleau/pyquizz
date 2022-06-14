"""Django settings for pyquizz project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# If the site has to be strong
SECRET_KEY = "%mi(v5@*=bf$7djarac)8%d0&po53t+3tdnepiuqoad4kn0)e#"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.amazon",
    "allauth.socialaccount.providers.apple",
    "allauth.socialaccount.providers.azure",
    "allauth.socialaccount.providers.coinbase",
    "allauth.socialaccount.providers.discord",
    "allauth.socialaccount.providers.disqus",
    "allauth.socialaccount.providers.dropbox",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.flickr",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.gitlab",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.instagram",
    "allauth.socialaccount.providers.linkedin_oauth2",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.nextcloud",
    "allauth.socialaccount.providers.openid",
    "allauth.socialaccount.providers.openstreetmap",
    "allauth.socialaccount.providers.patreon",
    "allauth.socialaccount.providers.paypal",
    "allauth.socialaccount.providers.pinterest",
    "allauth.socialaccount.providers.reddit",
    "allauth.socialaccount.providers.shopify",
    "allauth.socialaccount.providers.slack",
    "allauth.socialaccount.providers.snapchat",
    "allauth.socialaccount.providers.spotify",
    "allauth.socialaccount.providers.steam",
    "allauth.socialaccount.providers.telegram",
    "allauth.socialaccount.providers.twitch",
    "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.vimeo_oauth2",
    "allauth.socialaccount.providers.windowslive",
    "allauth.socialaccount.providers.yahoo",
    "allauth.socialaccount.providers.zoom",
    "quizz",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

# django-allauth
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[QCM] "
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 60
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 10
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
    # MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = ["127.0.0.1"]
    # SHOW_TOOLBAR_CALLBACK = True
else:
    ALLOWED_HOSTS = ["127.0.0.1", ".vpoulailleau.alwaysdata.net"]
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 60  # TODO 3600
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": "./debug_django.log",
                "mode": "a",
            }
        },
        "loggers": {
            "django": {
                "handlers": ["file"],
                "level": "DEBUG",
                "propagate": True,
            }
        },
    }


ROOT_URLCONF = "pyquizz.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "pyquizz.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATICFILES_DIRS = (os.path.join(BASE_DIR, "pyquizz/static"),)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static_collected")

MESSAGE_TAGS = {
    messages.DEBUG: "alert alert-warning",
    messages.INFO: "alert alert-secondary",
    messages.SUCCESS: "alert alert-success",
    messages.WARNING: "alert alert-warning",
    messages.ERROR: "alert alert-danger",
}
