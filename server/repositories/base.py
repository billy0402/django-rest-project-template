import typing as t
import uuid

from django import http
from django.db import models

Model = t.TypeVar("Model", bound=models.Model)


class BaseRepository(t.Generic[Model]):
    model: type[Model]

    def __init__(self, field_mappings: dict[str, str] | None = None) -> None:
        self.field_mappings = field_mappings or {}

    def _map_input_to_fields(self, data: dict[str, t.Any]) -> dict[str, t.Any]:
        mapped_data = {}
        for key, value in data.items():
            mapped_key = self.field_mappings.get(key, key)
            mapped_data[mapped_key] = value
        return mapped_data

    def _get_m2m_fields(self) -> dict[str, t.Any]:
        return {
            field.name: field.related_model
            for field in self.model._meta.get_fields()  # noqa: SLF001
            if field.many_to_many
        }

    def _extract_m2m_fields(
        self, data: dict[str, t.Any]
    ) -> tuple[dict[str, t.Any], dict[str, t.Any]]:
        processed_data = data.copy()
        m2m_fields = self._get_m2m_fields()
        m2m_data = {}
        for field_name in m2m_fields:
            if field_name in data:
                m2m_data[field_name] = data[field_name]
            processed_data.pop(field_name, None)
        return processed_data, m2m_data

    def _save_m2m_fields(self, instance: Model, data: dict[str, t.Any]) -> None:
        m2m_fields = self._get_m2m_fields()
        for field_name in m2m_fields:
            new_value = data.get(field_name, [])
            getattr(instance, field_name).set(new_value)

    def get_queryset(
        self,
        select_related: list[str] | None = None,
        prefetch_related: list[str] | None = None,
    ) -> models.QuerySet[Model]:
        queryset = self.model.objects.all()

        if select_related:
            queryset = queryset.select_related(*select_related)

        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        return queryset

    def get_all(
        self,
        select_related: list[str] | None = None,
        prefetch_related: list[str] | None = None,
    ) -> models.QuerySet[Model]:
        return self.get_queryset(select_related, prefetch_related)

    def get_by_id(
        self,
        pk: uuid.UUID | str,
    ) -> Model:
        try:
            queryset = self.get_queryset()
            return queryset.get(pk=pk)
        except self.model.DoesNotExist as e:
            raise http.Http404 from e

    def create(self, data: dict[str, t.Any]) -> Model:
        mapped_data = self._map_input_to_fields(data)
        processed_data, m2m_data = self._extract_m2m_fields(mapped_data)
        instance = self.model.objects.create(**processed_data)
        self._save_m2m_fields(instance, m2m_data)
        return self.get_by_id(instance.pk)

    def update(self, pk: uuid.UUID | str, data: dict[str, t.Any]) -> Model:
        mapped_data = self._map_input_to_fields(data)
        processed_data, m2m_data = self._extract_m2m_fields(mapped_data)

        instance = self.get_by_id(pk)
        for attr, value in processed_data.items():
            setattr(instance, attr, value)
        instance.save()

        self._save_m2m_fields(instance, m2m_data)

        return instance

    def delete(self, pk: uuid.UUID | str) -> None:
        obj = self.get_by_id(pk)
        obj.delete()

    def bulk_create(self, data_list: list[dict[str, t.Any]]) -> list[Model]:
        mapped_data_list = [self._map_input_to_fields(data) for data in data_list]

        processed_data_list, m2m_data_list = zip(
            *[self._extract_m2m_fields(data) for data in mapped_data_list], strict=False
        )
        instances = self.model.objects.bulk_create(
            [self.model(**processed_data) for processed_data in processed_data_list]
        )

        for instance, data in zip(instances, m2m_data_list, strict=False):
            self._save_m2m_fields(instance, data)

        return instances
