import typing as t

from django.db import models
from rest_framework import generics, serializers, viewsets

Model = t.TypeVar("Model", bound=models.Model)


class TypedGenericAPIView(generics.GenericAPIView, t.Generic[Model]):
    queryset: models.QuerySet[Model]

    def get_queryset(self) -> models.QuerySet[Model]:
        return t.cast(models.QuerySet[Model], super().get_queryset())


class TypedGenericViewSet(
    viewsets.GenericViewSet,
    TypedGenericAPIView[Model],
    t.Generic[Model],
):
    pass


class UserActionLogViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer: serializers.BaseSerializer) -> None:
        serializer.save(updated_by=self.request.user)


class BaseViewSet(TypedGenericViewSet[Model], t.Generic[Model]):
    def get_queryset(self) -> models.QuerySet[Model]:
        queryset = super().get_queryset()

        if self.action in ["list", "retrieve"]:
            serializer = self.get_serializer()
            fields: dict[str, t.Any] | None = getattr(serializer, "fields", None)
            if fields and "created_by" in fields:
                queryset = queryset.select_related("created_by")
            if fields and "updated_by" in fields:
                queryset = queryset.select_related("updated_by")

        return queryset
