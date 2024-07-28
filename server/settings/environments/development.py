import datetime

from server.settings import INSTALLED_APPS, MIDDLEWARE
from server.settings.components.jwt import NINJA_JWT

DEVELOPMENT_APPS = [
    "nplusone.ext.django",
]

DEVELOPMENT_MIDDLEWARE = [
    "nplusone.ext.django.NPlusOneMiddleware",
]


INSTALLED_APPS += DEVELOPMENT_APPS
MIDDLEWARE += DEVELOPMENT_MIDDLEWARE

NPLUSONE_RAISE = True

NINJA_JWT["ACCESS_TOKEN_LIFETIME"] = datetime.timedelta(days=1)
