import typing as t

from django.contrib import auth
from django.contrib.auth import models as auth_models

from server.utils.django.models import base as base_models


class User(auth_models.AbstractUser, base_models.BaseModel):
    pass


UserModel = t.cast(User, auth.get_user_model())
