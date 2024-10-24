from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from server.app.authentication import models as auth_models


@admin.register(auth_models.User)
class UserAdmin(auth_admin.UserAdmin):
    pass
