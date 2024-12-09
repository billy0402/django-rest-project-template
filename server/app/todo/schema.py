import datetime
import typing as t

import pydantic
from ninja import schema

from server.utils.ninja.schema import mixins as schema_mixins


class Tag(schema.Schema):
    id: pydantic.UUID4
    name: str


class Category(schema.Schema):
    id: pydantic.UUID4
    name: str


class Task(schema_mixins.BaseMixin):
    title: str
    description: str | None
    is_finish: bool
    tags: list[Tag]
    category: Category | None = None
    attachment: str | None = None
    end_at: datetime.datetime | None = None


class TaskCreate(schema.Schema):
    title: str = schema.Field(min_length=1)
    description: str = ""
    is_finish: bool | None = False
    tag_ids: t.ClassVar[list[pydantic.UUID4]] = []
    category_id: pydantic.UUID4 | None = None
    attachment: str | None = None
    end_at: str | None = None
