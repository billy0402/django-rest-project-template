# pyright: basic
# pyright: reportGeneralTypeIssues=false

"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import pathlib
import sys
import warnings

import django_stubs_ext
import environ
from django.utils import deprecation
from split_settings import tools as split_settings

warnings.filterwarnings("ignore", category=deprecation.RemovedInDjango60Warning)  # pyright: ignore[reportAttributeAccessIssue]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env.prefix = "DJANGO_"

if (env_file := BASE_DIR / "server" / "settings" / ".env").exists():
    env.read_env(env_file=env_file)


# Monkeypatching Django, so stubs will work for all generics,
# see: https://github.com/typeddjango/django-stubs
django_stubs_ext.monkeypatch()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = env.str("SECRET_KEY")

ENV: str = "test" if "pytest" in sys.modules else env.str("ENV", default="production")  # pyright: ignore[reportArgumentType]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = env.bool("DEBUG", default=(ENV != "production"))  # pyright: ignore[reportArgumentType]

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=[])  # pyright: ignore[reportArgumentType]

CORS_ALLOWED_ORIGINS: list[str] = env.list("CORS_ALLOWED_ORIGINS", default=[])  # pyright: ignore[reportArgumentType]


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "corsheaders",
    "ninja",
    "ninja_extra",
    "ninja_jwt",
]

LOCAL_APPS = [
    "server.app.common",
    "server.app.authentication",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

URL_PREFIX: str = env.str("URL_PREFIX", default="")  # pyright: ignore[reportArgumentType]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "server" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="postgres://postgres@localhost:5432/postgres",  # pyright: ignore[reportArgumentType]
    ),
}

FIXTURE_DIRS = [
    BASE_DIR / "server" / "fixtures",
]


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "authentication.User"


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = f"{URL_PREFIX}static/"

STATICFILES_DIRS = [
    BASE_DIR / "server" / "static",
]

STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = f"{URL_PREFIX}media/"

MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "server.utils.django.fields.UUIDAutoField"


# Extra settings

split_settings.include(
    "components/*.py",
    f"environments/{ENV}.py",
)
