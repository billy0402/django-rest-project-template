from django.contrib.auth import models as auth_models

from server.utils.django import models as util_models


class CustomUser(auth_models.AbstractUser, util_models.UUIDModel):
    pass
