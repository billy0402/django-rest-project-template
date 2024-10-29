from django.db import models
from django.utils import timezone


class SoftDeletableQuerySet(models.QuerySet[models.Model]):
    def delete(self) -> None:
        self.update(deleted_at=timezone.now())

    def undelete(self) -> None:
        self.update(deleted_at=None)


class SoftDeletableManager(models.Manager[models.Model]):
    _queryset_class = SoftDeletableQuerySet

    def get_queryset(self) -> models.QuerySet[models.Model]:
        return super().get_queryset().filter(deleted_at__isnull=True)


class GlobalQuerySet(models.QuerySet[models.Model]):
    def undelete(self) -> None:
        self.update(deleted_at=None)


class GlobalManager(models.Manager):
    _queryset_class = GlobalQuerySet
