"""
Django settings for hostinfo project.

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "<CHANGEME>"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
with open(os.path.join(BASE_DIR, "..", "version"), encoding="utf-8") as versfh:
    VERSION = versfh.read().strip()

ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1"]

LOGIN_REDIRECT_URL = "/hostinfo/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        }
    },
}

# Will print queries and their times to console
if "DEBUG_DJANGO_DB" in os.environ:  # pragma: no cover
    LOGGING["loggers"] = {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        }
    }

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",
    "host",
    "hostinfo",
    "report",
]
if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]
if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "hostinfo.urls"

WSGI_APPLICATION = "hostinfo.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "hostinfo",
        "USER": "hostinfo",
        "PASSWORD": "hostinfo",
        "HOST": "localhost",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

USE_TZ = False

HOSTINFO_REPORT_DIR = "/tmp/reports"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

STATIC_URL = "/static/"
STATIC_ROOT = "/opt/hostinfo/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
