from django.db import models

from server.utils.django import fields as util_fields
from server.utils.django.models import base as base_models


class MockModel(base_models.BaseModel):
    name = models.CharField(max_length=100)


class MockSoftDeletableModel(base_models.SoftDeletableModel):
    name = models.CharField(max_length=100)


class ModelWithoutCreatedAt(models.Model):
    updated_at = util_fields.UpdatedAtField()

    def __str__(self) -> str:
        return f"{self.updated_at}"
