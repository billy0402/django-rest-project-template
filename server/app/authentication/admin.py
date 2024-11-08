from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from server.app.authentication import models as auth_models
from server.utils.django import admin as util_admin


@admin.register(auth_models.User)
class UserAdmin(util_admin.BaseAdmin, auth_admin.UserAdmin):
    readonly_fields = (
        *auth_admin.UserAdmin.readonly_fields,
        "last_login",
        "date_joined",
    )
