from collections.abc import Sequence

from django.db.models.query import QuerySet

from server.utils.django import models as util_models


class OptimizeQuerysetMixin:
    select_related_fields: Sequence[str] = ()
    prefetch_related_fields: Sequence[str] = ()

    def get_queryset(self) -> QuerySet[util_models.BaseModel]:
        queryset: QuerySet[util_models.BaseModel] = super().get_queryset()
        if not isinstance(queryset, QuerySet):
            raise TypeError("Expected queryset to be a QuerySet")

        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        return queryset
