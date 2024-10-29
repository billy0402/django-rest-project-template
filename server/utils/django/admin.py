import typing as t

from django import forms
from django.contrib import admin
from django.db import models
from django.http import request
from django.utils.translation import gettext_lazy as _

from server.utils.django.models import base as base_models


class BaseAdmin(admin.ModelAdmin[base_models.BaseModel]):
    readonly_fields = ("created_by", "updated_by")

    def save_model(
        self,
        request: request.HttpRequest,
        obj: base_models.BaseModel,
        form: forms.ModelForm,
        change: bool,  # noqa: FBT001
    ) -> None:
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


def delete_selected(
    modeladmin: admin.ModelAdmin[base_models.SoftDeletableModel],
    request: request.HttpRequest,
    queryset: models.QuerySet[base_models.SoftDeletableModel],
) -> None:
    for obj in queryset.all():
        obj.delete()


class SoftDeletableAdmin(admin.ModelAdmin[base_models.SoftDeletableModel]):
    @admin.display(boolean=True)
    def is_deleted(self, obj: base_models.SoftDeletableModel) -> bool:
        return obj.deleted_at is not None

    is_deleted.short_description = _("delete status")

    def get_list_display(self, request: request.HttpRequest) -> t.Sequence[t.Any]:
        return [*self.list_display, "is_deleted"]

    def get_queryset(
        self, request: request.HttpRequest
    ) -> models.QuerySet[base_models.SoftDeletableModel]:
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
