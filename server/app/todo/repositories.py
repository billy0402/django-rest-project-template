from server.app.todo import models as todo_models
from server.repositories import base as base_repository


class TaskRepository(base_repository.BaseRepository):
    model = todo_models.Task
