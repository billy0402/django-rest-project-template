from server.settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE

TEST_APPS = [
    "nplusone.ext.django",
    "server.utils.django.tests",
]

TEST_MIDDLEWARE = [
    "nplusone.ext.django.NPlusOneMiddleware",
]


INSTALLED_APPS += TEST_APPS
MIDDLEWARE += TEST_MIDDLEWARE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "TEST": {
            "NAME": BASE_DIR / "db_test.sqlite3",
        },
    }
}
AUTH_PASSWORD_VALIDATORS = []
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
TIME_ZONE = "UTC"

NPLUSONE_RAISE = True
