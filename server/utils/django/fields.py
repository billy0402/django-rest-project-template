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
