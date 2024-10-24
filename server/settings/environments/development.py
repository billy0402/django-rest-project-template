import datetime

from server.settings import INSTALLED_APPS, MIDDLEWARE
from server.settings.components.simple_jwt import SIMPLE_JWT

DEVELOPMENT_APPS = [
    "nplusone.ext.django",
]

DEVELOPMENT_MIDDLEWARE = [
    "nplusone.ext.django.NPlusOneMiddleware",
]


INSTALLED_APPS += DEVELOPMENT_APPS
MIDDLEWARE += DEVELOPMENT_MIDDLEWARE

NPLUSONE_RAISE = True

SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = datetime.timedelta(days=1)
