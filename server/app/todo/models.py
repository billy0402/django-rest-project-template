import typing as t

from django.contrib import auth
from django.db import models

from server.utils.django.models import base as base_models

User = auth.get_user_model()


class Category(base_models.BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Tag(base_models.BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Task(base_models.BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_finish = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    tags: models.ManyToManyField[Tag, t.Self] = models.ManyToManyField(Tag)
    attachment = models.FileField(null=True, upload_to="task/attachments")
    end_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.title
