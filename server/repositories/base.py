import typing as t

from django.db import models
from django.db.models import manager

Model = t.TypeVar("Model", bound=models.Model)


class BaseRepository(t.Generic[Model]):
    model: type[Model]

    def __init__(self, model: type[Model]) -> None:
        self.model = model

    def get_all(
        self,
        select_related: list[str] | None = None,
        prefetch_related: list[str] | None = None,
    ) -> manager.BaseManager[Model]:
        qs = self.model.objects.all()
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)
        return qs

    def get_by_id(
        self,
        id_: int,
        select_related: list[str] | None = None,
        prefetch_related: list[str] | None = None,
    ) -> Model | None:
        qs = self.model.objects
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)
        return qs.filter(pk=id_).first()

    def create(self, **data: t.Any) -> Model:
        return self.model.objects.create(**data)
