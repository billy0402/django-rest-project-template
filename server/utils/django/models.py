import uuid

from django.conf import settings
from django.db import models

from server.utils.django import fields as util_fields


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampModel(models.Model):
    created_at = util_fields.CreatedAtField()
    updated_at = util_fields.UpdatedAtField()

    class Meta:
        abstract = True


class EditorModel(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="creator",
    )
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="editor",
    )

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampModel, EditorModel):
    class Meta:
        abstract = True
