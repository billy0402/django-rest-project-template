import datetime
import typing as t

from django import http
from django.conf import settings
from django.http import response
from django.utils import timezone
from ninja import Schema
from ninja import errors as e
from ninja_extra import NinjaExtraAPI
from ninja_extra import exceptions as ee


class ErrorResponse(Schema):
    status_code: int
    detail: str
    code: str
    messages: t.Any | None
    timestamp: datetime.datetime


def custom_exception_handler(
    request: http.HttpRequest,
    exc: Exception | type[Exception],
) -> response.HttpResponse:
    """Return Error Response.

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
    if isinstance(exc, e.ValidationError):  # 400
        message = exc.errors
        exc = ee.ValidationError()
        exc.message = t.cast(t.Any, message)

    if isinstance(exc, e.AuthenticationError):  # 401
        exc = ee.AuthenticationFailed()

    if isinstance(exc, http.Http404):  # 404
        exc = ee.NotFound()

    if not isinstance(exc, ee.APIException):  # 500
        if settings.DEBUG:
            raise exc

        data = ErrorResponse(
            status_code=ee.APIException.status_code,
            detail=str(ee.APIException.default_detail),
            code=ee.APIException.default_code,
            messages=exc.args,
            timestamp=timezone.now(),
        )
        return response.JsonResponse(data.dict(), status=data.status_code)

    data = ErrorResponse(
        status_code=exc.status_code,
        detail=str(exc.default_detail),
        code=exc.default_code,
        messages=getattr(exc, "message", None),
        timestamp=timezone.now(),
    )
    return response.JsonResponse(data.dict(), status=data.status_code)


def register_exception_handler(app: NinjaExtraAPI) -> None:
    app.add_exception_handler(e.AuthenticationError, custom_exception_handler)  # 400
    app.add_exception_handler(e.ValidationError, custom_exception_handler)  # 401
    app.add_exception_handler(http.Http404, custom_exception_handler)  # 404
    app.add_exception_handler(ee.APIException, custom_exception_handler)  # 500
    app.add_exception_handler(e.HttpError, custom_exception_handler)  # 500
    app.add_exception_handler(Exception, custom_exception_handler)  # 500
