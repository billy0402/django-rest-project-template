import typing as t

from django import forms
from django.contrib import admin
from django.db import models
from django.http import request
from django.utils.translation import gettext_lazy as _

from server.utils.django.models import base as base_models

meta_fields = ("created_at", "updated_at", "created_by", "updated_by")
meta_fields_set = set(meta_fields)


class BaseAdmin(admin.ModelAdmin[base_models.BaseModel]):
    def get_list_display(self, request: request.HttpRequest) -> t.Sequence[str]:
        list_display = super().get_list_display(request)
        return (*list_display, *meta_fields)

    def get_readonly_fields(
        self,
        request: request.HttpRequest,
        obj: base_models.BaseModel | None = None,
    ) -> t.Sequence[t.Any]:
        readonly_fields = super().get_readonly_fields(request, obj)
        return (*meta_fields, *readonly_fields)

    def get_fieldsets(
        self,
        request: request.HttpRequest,
        obj: base_models.BaseModel | None = None,
    ) -> list[tuple[str | None, dict[str, t.Any]]]:
        fieldsets = super().get_fieldsets(request, obj)
        if not self.fieldsets:
            fields = super().get_fields(request, obj)
            fields = [f for f in fields if f not in meta_fields_set]
            fieldsets = [(None, {"fields": fields})]

        return [
            *fieldsets,
            (_("Metadata"), {"fields": meta_fields}),
        ]

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
