import typing as t

from django.db import models
from rest_framework import mixins, request, serializers, viewsets

Model = t.TypeVar("Model", bound=models.Model)
Serializer = t.TypeVar("Serializer", bound=serializers.BaseSerializer)


class CreateUserActionLogMixin(mixins.CreateModelMixin):
    request: request.Request

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class UpdateUserActionLogMixin(mixins.UpdateModelMixin):
    request: request.Request

    def perform_update(self, serializer: serializers.BaseSerializer) -> None:
        serializer.save(updated_by=self.request.user)


class BaseGenericViewSet(t.Generic[Model, Serializer], viewsets.GenericViewSet):
    queryset: models.QuerySet[Model]
    serializer_class: type[Serializer]

    def get_queryset(self) -> models.QuerySet[Model]:
        queryset = super().get_queryset()

        if self.action in ["list", "retrieve"]:
            serializer = self.get_serializer()
            fields = getattr(serializer, "fields", {})
            if "created_by" in fields:
                queryset = queryset.select_related("created_by")
            if "updated_by" in fields:
                queryset = queryset.select_related("updated_by")

        return queryset
