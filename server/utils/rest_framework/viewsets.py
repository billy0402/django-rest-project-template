import typing as t

from django.db import models
from rest_framework import generics, viewsets

from server.typings import rest_framework as drft

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


class BaseViewSet(TypedGenericViewSet[Model], t.Generic[Model]):
    request: drft.AuthenticatedRequest

    def get_queryset(self) -> models.QuerySet[Model]:
        queryset = super().get_queryset()

        if self.action in ["list", "retrieve"]:
            serializer = self.get_serializer()
            fields: dict[str, t.Any] | None = getattr(serializer, "fields", None)
            if fields and "creator" in fields:
                queryset = queryset.select_related("creator")
            if fields and "editor" in fields:
                queryset = queryset.select_related("editor")

        return queryset
