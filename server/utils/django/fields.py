import datetime
import typing as t
import uuid

from django.db import models
from django.db.backends.base import operations as base_operations

base_operations.BaseDatabaseOperations.integer_field_ranges["UUIDField"] = (0, 0)


class UUIDAutoField(models.UUIDField[uuid.UUID], models.AutoField):  # pyright: ignore[reportGeneralTypeIssues]
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        kwargs.setdefault("default", uuid.uuid4)
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)


class CreatedAtField(models.DateTimeField[datetime.datetime]):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        kwargs["auto_now_add"] = True
        super().__init__(*args, **kwargs)


class UpdatedAtField(models.DateTimeField[datetime.datetime]):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        kwargs["auto_now"] = True
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance: models.Model, add: bool) -> datetime.datetime:  # noqa: FBT001
        if add:
            for field in model_instance._meta.get_fields():  # noqa: SLF001
                if not isinstance(field, CreatedAtField):
                    continue

                value = getattr(model_instance, field.name)
                setattr(model_instance, self.attname, value)
                return value

        return super().pre_save(model_instance, add)
