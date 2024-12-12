import typing as t
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from server.utils.django import fields as util_fields
from server.utils.django import managers


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedTimestampMixin(models.Model):
    created_at = util_fields.CreatedAtField()

    class Meta:
        abstract = True


class UpdatedTimestampMixin(models.Model):
    updated_at = util_fields.UpdatedAtField()

    class Meta:
        abstract = True


class TimestampMixin(CreatedTimestampMixin, UpdatedTimestampMixin):
    class Meta:
        abstract = True


class CreatedActionLogMixin(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_created_by",
        null=True,
        editable=False,
    )

    class Meta:
        abstract = True


class UpdatedActionLogMixin(models.Model):
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_updated_by",
        null=True,
        editable=False,
    )

    class Meta:
        abstract = True


class UserActionLogMixin(CreatedActionLogMixin, UpdatedActionLogMixin):
    class Meta:
        abstract = True


class BaseModel(UUIDPrimaryKeyMixin, TimestampMixin, UserActionLogMixin):
    class Meta:
        abstract = True
        ordering = ("-created_at",)


class SoftDeletableModel(models.Model):
    deleted_at = models.DateTimeField(
        null=True,
        default=None,
        editable=False,
        db_index=True,
    )

    all_objects = managers.GlobalManager()
    objects = managers.SoftDeletableManager()

    class Meta:
        abstract = True

    def delete(
        self,
        using: str | None = None,
        soft: bool = True,  # noqa: FBT001, FBT002
        *args: t.Any,
        **kwargs: t.Any,
    ) -> tuple[int, dict[str, int]]:
        if not soft:
            return super().delete(*args, using=using, **kwargs)

        self.deleted_at = timezone.now()
        self.save(using=using)
        return 0, {}

    def undelete(self, using: str | None = None, *args: t.Any, **kwargs: t.Any) -> None:
        self.deleted_at = None
        self.save(using=using)
