import abc
import typing as t

from django.db import models

Model = t.TypeVar("Model", bound=models.Model)


class BaseRepository(abc.ABC, t.Generic[Model]):
    model: type[Model]
    queryset: models.QuerySet[Model]

    def __init__(self) -> None:
        if type(self) is BaseRepository:
            msg = f"{self.__class__.__name__} is an abstract class and cannot be instantiated."  # noqa: E501
            raise TypeError(msg)
