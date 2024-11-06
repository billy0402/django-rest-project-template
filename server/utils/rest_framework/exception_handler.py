import datetime
import typing as t

from django.conf import settings
from django.http import Http404
from django.utils import timezone
from rest_framework import exceptions, views
from rest_framework import response as drf_response


class ErrorResponse(t.TypedDict):
    status_code: int
    detail: str
    code: str
    messages: t.Any
    timestamp: datetime.datetime


def custom_exception_handler(
    exception: Exception,
    context: dict[str, t.Any],
) -> drf_response.Response:
    """
    Custom exception handler for Django REST Framework.

    Args:
        exception (Exception): The exception that was raised.
        context (dict[str, t.Any]): The context of the exception.

    Returns:
        drf_response.Response: The response object.

    Raises:
        exception: If settings.DEBUG is True.

    Example:
    {
        "status_code": 401,
        "detail": "Given token not valid for any token type",
        "code": "token_not_valid",
        "messages": [
            {
                "token_class": "AccessToken",
                "token_type": "access",
                "message": "Token is invalid or expired"
            }
        ],
        "timestamp": "2024-06-13T03:27:36.685027Z"
    }
    """
    if isinstance(exception, Http404):
        exception = exceptions.NotFound()

    response = views.exception_handler(exception, context)

    if response and isinstance(exception, exceptions.APIException):
        if not isinstance(response.data, dict):
            response.data = {"detail": response.data}

        data: ErrorResponse = {
            "status_code": exception.status_code,
            "detail": exception.default_detail,
            "code": exception.default_code,
            "messages": response.data.get("messages", response.data),
            "timestamp": timezone.now(),
        }
        return drf_response.Response(data, status=data["status_code"], exception=True)

    if settings.DEBUG:
        raise exception

    data: ErrorResponse = {
        "status_code": exceptions.APIException.status_code,
        "detail": exceptions.APIException.default_detail,
        "code": exceptions.APIException.default_code,
        "messages": exception.args,
        "timestamp": timezone.now(),
    }
    return drf_response.Response(data, status=data["status_code"], exception=True)
