import uuid

import ninja
from django.db import models
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
    http_put,
    paginate,
    status,
)

from server.app.todo import models as todo_models
from server.app.todo import repositories as todo_repositories
from server.app.todo import schema as todo_schema
from server.utils.ninja import pagination


@api_controller("/todo/tasks", tags=["todo"])
class TaskController(ControllerBase):
    repository = todo_repositories.TaskRepository(
        field_mappings={"tag_ids": "tags"},
    )

    @http_get("", response=pagination.PaginationOut[todo_schema.Task])
    @paginate()
    def list(self) -> models.QuerySet[todo_models.Task]:
        return self.repository.get_all(
            select_related=["category", "created_by", "updated_by"],
            prefetch_related=["tags"],
        )

    @http_get("/{id_}", response=todo_schema.Task)
    def retrieve(self, id_: uuid.UUID) -> todo_models.Task:
        return self.repository.get_by_id(id_)

    @http_post("", response={status.HTTP_201_CREATED: todo_schema.Task})
    def create(self, payload: todo_schema.TaskCreate) -> tuple[int, todo_models.Task]:
        data = payload.dict()
        request_user = self.context.request.user  # pyright: ignore[reportOptionalMemberAccess]
        data["created_by"] = request_user
        data["updated_by"] = request_user
        return status.HTTP_201_CREATED, self.repository.create(data)

    @http_put("/{id_}", response=todo_schema.Task)
    def update(
        self,
        id_: uuid.UUID,
        payload: todo_schema.TaskCreate,
    ) -> todo_models.Task:
        return self.repository.update(id_, payload.dict())

    @http_patch("/{id_}", response=todo_schema.Task)
    def partial_update(
        self,
        id_: uuid.UUID,
        payload: ninja.PatchDict[todo_schema.TaskCreate],  # pyright: ignore[reportInvalidTypeArguments]
    ) -> todo_models.Task:
        return self.repository.update(id_, payload)

    @http_delete("/{id_}", response={status.HTTP_204_NO_CONTENT: None})
    def delete_task(self, id_: uuid.UUID) -> tuple[int, None]:
        self.repository.delete(id_)
        return status.HTTP_204_NO_CONTENT, None
