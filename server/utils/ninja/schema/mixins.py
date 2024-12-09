import datetime

import pydantic
from ninja import schema


class UUIDMixin(schema.Schema):
    id: pydantic.UUID4


class CreateTimestampMixin(schema.Schema):
    created_at: datetime.datetime


class UpdateTimestampMixin(schema.Schema):
    updated_at: datetime.datetime


class TimestampMixin(UpdateTimestampMixin, CreateTimestampMixin):
    pass


class MeatUser(schema.Schema):
    id: pydantic.UUID4
    username: str
    first_name: str
    last_name: str


class UserActionLogMixin(schema.Schema):
    created_by: MeatUser | None
    updated_by: MeatUser | None


class BaseMixin(UserActionLogMixin, TimestampMixin, UUIDMixin):
    pass
