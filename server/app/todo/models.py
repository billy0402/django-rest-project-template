import typing as t

from django.contrib import auth
from django.db import models

from server.utils.django import fields as util_fields

User = auth.get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_finish = models.BooleanField(default=False)
    tags: models.ManyToManyField[Tag, t.Self] = models.ManyToManyField(Tag)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    attachment = models.FileField(blank=True, upload_to="task/attachments")
    end_at = models.DateTimeField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = util_fields.CreatedAtField()
    updated_at = util_fields.UpdatedAtField()

    def __str__(self) -> str:
        return self.title
