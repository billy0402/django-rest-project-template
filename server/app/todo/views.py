from django.shortcuts import get_object_or_404
from ninja_extra import (
    api_controller,  # type: ignore
    http_delete,
    http_get,
    http_patch,
    http_post,
    http_put,
    paginate,
)
from ninja_jwt.authentication import JWTAuth  # type: ignore

from server.app.todo import models as todo_models
from server.app.todo import schema as todo_schema
from server.repositories import base as base_repository
from server.utils.ninja import pagination


@api_controller("/todo/tasks", tags=["todo"])
class TaskController:
    repository = base_repository.BaseRepository(todo_models.Task)

    @http_get(
        "",
        response=pagination.PaginationOut[todo_schema.Task],
    )
    @paginate()
    def list(self):
        return self.repository.get_all(
            select_related=["category", "creator"],
            prefetch_related=["tags"],
        )
        query_set = todo_models.Task.objects.select_related(
            "category",
            "creator",
        ).prefetch_related("tags")
        return query_set

    @http_get(
        "/{id_}",
        response=todo_schema.Task,
    )
    def retrieve(self, id_: int):
        return self.repository.get_by_id(
            id_,
            select_related=["category", "creator"],
            prefetch_related=["tags"],
        )

    @http_post(
        "",
        response=todo_schema.Task,
        auth=JWTAuth(),
    )
    def create(self, payload: todo_schema.TaskCreate):
        user = self.context.request.auth
        data = payload.dict(exclude={"tag_ids"})
        data["creator"] = user
        task = todo_models.Task.objects.create(**data)
        if payload.tag_ids:
            task.tags.set(payload.tag_ids)  # type: ignore
        return task

    @http_put("/{id_}", response=todo_schema.Task)
    def update(self, id_: int, payload: todo_schema.TaskUpdate):
        task = get_object_or_404(todo_models.Task, id=id_)
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(task, attr, value)
        task.save()
        if "tag_ids" in payload.dict(exclude_unset=True):
            task.tags.set(payload.tag_ids)  # type: ignore
        return task

    @http_patch("/{id_}", response=todo_schema.Task)
    def partial_update(self, id_: int, payload: todo_schema.TaskUpdate):
        task = get_object_or_404(todo_models.Task, id=id_)
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(task, attr, value)
        task.save()
        if "tag_ids" in payload.dict(exclude_unset=True):
            task.tags.set(payload.tag_ids)  # type: ignore
        return task

    @http_delete("/{id_}", response=None)
    def delete_task(self, id_: int):
        data = get_object_or_404(todo_models.Task, id=id_)
        data.delete()
        return 204
