from django import forms, http
from django.contrib import admin

from server.utils.django import models as util_models


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ("creator", "editor")

    def save_model(
        self,
        request: http.HttpRequest,
        obj: util_models.BaseModel,
        form: forms.Form,
        change: bool,
    ):
        if not change:
            obj.creator = request.user
        obj.editor = request.user
        super().save_model(request, obj, form, change)
