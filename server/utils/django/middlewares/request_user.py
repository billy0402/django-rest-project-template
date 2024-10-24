import threading
import typing as t

from django.contrib.auth import models as django_auth_models
from django.http import request, response
from django.utils.functional import SimpleLazyObject

_thread_local = threading.local()


class RequestUserMiddleware:
    def __init__(
        self,
        get_response: t.Callable[[request.HttpRequest], response.HttpResponse],
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: request.HttpRequest) -> response.HttpResponse:
        _thread_local.user = SimpleLazyObject(lambda: request.user)
        return self.get_response(request)


def get_request_user() -> object | None:
    request_user = _thread_local.user
    if callable(request_user):
        return request_user()
    if isinstance(request_user, django_auth_models.AnonymousUser):
        return None
    return request_user
