import typing as t

from django.urls import URLResolver
from ninja_extra import NinjaExtraAPI

from server.app.authentication import views as auth_views
from server.app.common.views import router as common_router
from server.app.todo import views as todo_views

api_docs_settings: dict[str, t.Any] = {
    "title": "Django REST project API",
    "description": "This is a demo API with dynamic OpenAPI info section",
}

api = NinjaExtraAPI(
    **api_docs_settings,
    version="1.0.0",
    urls_namespace="api-v1",
)

api.register_controllers(auth_views.AuthTokenController)
api.register_controllers(todo_views.TaskController)
api.add_router("_", common_router, tags=["common"])

api_urls = t.cast(tuple[list[URLResolver], str, str], api.urls)
