from django.contrib import admin

from server.app.authentication import models as auth_models


@admin.register(auth_models.CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass
