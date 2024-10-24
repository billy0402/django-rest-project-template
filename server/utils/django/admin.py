import typing as t

from django.contrib import admin
from django.db import models
from django.http import request
from django.utils.translation import gettext_lazy as _

from server.utils.django.models import base as base_models
from server.utils.django.models import utils as util_models


def delete_selected(
    modeladmin: admin.ModelAdmin[util_models.SoftDeletableModel],
    request: request.HttpRequest,
    queryset: models.QuerySet[util_models.SoftDeletableModel],
) -> None:
    for obj in queryset.all():
        obj.delete()


class SoftDeletableAdmin(admin.ModelAdmin[util_models.SoftDeletableModel]):
    @admin.display(boolean=True)
    def is_deleted(self, obj: util_models.SoftDeletableModel) -> bool:
        return obj.deleted_at is not None

    is_deleted.short_description = _("delete status")

    def get_list_display(self, request: request.HttpRequest) -> t.Sequence[t.Any]:
        return [*self.list_display, "is_deleted"]

    def get_queryset(
        self, request: request.HttpRequest
    ) -> models.QuerySet[util_models.SoftDeletableModel]:
        qs = t.cast(
            models.QuerySet[util_models.SoftDeletableModel],
            self.model.all_objects.get_queryset(),
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class BaseAdmin(admin.ModelAdmin[base_models.BaseModel]):
    readonly_fields = ("creator", "editor")
