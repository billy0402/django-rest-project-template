from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from server.app.authentication import models as auth_models
from server.utils.django import admin as util_admin


@admin.register(auth_models.User)
class UserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        *auth_admin.UserAdmin.fieldsets,
        (_("User action log"), {"fields": util_admin.BaseAdmin.readonly_fields}),  # pyright: ignore[reportAssignmentType]
    )
    readonly_fields = (
        *util_admin.BaseAdmin.readonly_fields,
        "last_login",
        "date_joined",
    )
