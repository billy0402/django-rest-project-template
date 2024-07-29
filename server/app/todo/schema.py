# Pydantic Schemas

import datetime
import uuid

from ninja import Schema


class User(Schema):
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
    last_login: datetime.datetime
    date_joined: datetime.datetime


class Tag(Schema):
    id: int
    name: str
    description: str | None = None


class Category(Schema):
    id: int
    name: str


class Task(Schema):
    id: int
    title: str
    description: str | None = None
    is_finish: bool
    tags: list[Tag]
    category: Category
    attachment: str | None = None  # Assuming it will be a URL
    end_at: str | None = None  # ISO 8601 format datetime string
    creator: User
    created_at: datetime.datetime
    updated_at: datetime.datetime


class TaskCreate(Schema):
    title: str
    description: str | None = None
    is_finish: bool | None = False
    tag_ids: list[int]  # list of Tag IDs
    category_id: int  # Category ID
    attachment: str | None = None
    end_at: str | None = None


class TaskUpdate(Schema):
    title: str | None = None
    description: str | None = None
    is_finish: bool | None = None
    tag_ids: list[int] | None = None
    category_id: int | None = None
    attachment: str | None = None
    end_at: str | None = None
