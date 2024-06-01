import datetime
import uuid
from typing import Any

from django.db import models
from django.db.backends.base.operations import BaseDatabaseOperations

BaseDatabaseOperations.integer_field_ranges["UUIDField"] = (0, 0)


class UUIDAutoField(models.UUIDField, models.AutoField):
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]):
        kwargs.setdefault("default", uuid.uuid4)
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)


class CreatedAtField(models.DateTimeField):
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]):
        kwargs["auto_now_add"] = True
        super().__init__(*args, **kwargs)


class UpdatedAtField(models.DateTimeField):
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]):
        kwargs["auto_now"] = True
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance: models.Model, add: bool) -> datetime.datetime:
        if add:
            for field in model_instance._meta.get_fields():
                if not isinstance(field, CreatedAtField):
                    continue

                value = getattr(model_instance, field.name)
                setattr(model_instance, self.attname, value)
                return value

        return super().pre_save(model_instance, add)
