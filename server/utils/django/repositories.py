import abc
import typing as t

from django.db import models

Model = t.TypeVar("Model", bound=models.Model)


class BaseRepository(abc.ABC, t.Generic[Model]):
    model: type[Model]
    queryset: models.QuerySet[Model]
