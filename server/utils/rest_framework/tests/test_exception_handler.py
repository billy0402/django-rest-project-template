import datetime
import typing as t
from unittest.mock import patch

import pytest
from rest_framework import exceptions, request, status, test
from rest_framework import response as drf_response

from server.utils.rest_framework.exception_handler import custom_exception_handler


@pytest.fixture
def mock_context() -> dict[str, request.Request]:
    factory = test.APIRequestFactory()
    request = factory.get("/")
    return {"request": request}


class TestCustomExceptionHandler:
    def test_handles_api_exception(
        self,
        mock_context: dict[str, request.Request],
    ) -> None:
        exception = exceptions.AuthenticationFailed("Authentication failed")

        response = custom_exception_handler(exception, mock_context)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data["status_code"] == status.HTTP_401_UNAUTHORIZED
        assert response_data["detail"] == "Incorrect authentication credentials."
        assert response_data["code"] == "authentication_failed"
        assert response_data["messages"]["detail"] == "Authentication failed"
        assert isinstance(response_data["timestamp"], datetime.datetime)

    def test_handles_api_exception_with_custom_messages(
        self,
        mock_context: dict[str, request.Request],
    ) -> None:
        exception = exceptions.ValidationError(
            {
                "messages": [
                    {"field": "email", "message": "Invalid email format"},
                    {"field": "password", "message": "Password too short"},
                ]
            }
        )

        response = custom_exception_handler(exception, mock_context)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_data["status_code"] == status.HTTP_400_BAD_REQUEST
        assert response_data["code"] == "invalid"
        assert len(response_data["messages"]) == 2  # noqa: PLR2004
        assert response_data["messages"][0]["field"] == "email"

    def test_handles_non_dict_response_data(
        self,
        mock_context: dict[str, request.Request],
    ) -> None:
        exception = exceptions.NotAuthenticated("Please authenticate")
        with patch("rest_framework.views.exception_handler") as mock_handler:
            mock_response = drf_response.Response("Raw error message")
            mock_handler.return_value = mock_response

            response = custom_exception_handler(exception, mock_context)
            response_data = t.cast(dict[str, t.Any], response.data)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert (
                response_data["detail"]
                == "Authentication credentials were not provided."
            )
            assert response_data["messages"]["detail"] == "Raw error message"

    @pytest.mark.parametrize("debug_setting", [True, False])
    def test_handles_generic_exception(
        self,
        debug_setting: bool,  # noqa: FBT001
        mock_context: dict[str, request.Request],
    ) -> None:
        exception = ValueError("Something went wrong")

        with patch("django.conf.settings.DEBUG", debug_setting):
            if debug_setting:
                with pytest.raises(ValueError, match="Something went wrong"):
                    custom_exception_handler(exception, mock_context)
            else:
                response = custom_exception_handler(exception, mock_context)
                response_data = t.cast(dict[str, t.Any], response.data)

                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert (
                    response_data["status_code"]
                    == status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                assert response_data["code"] == "error"
                assert response_data["messages"] == ("Something went wrong",)
                assert isinstance(response_data["timestamp"], datetime.datetime)

    def test_handles_nested_api_exception_data(
        self,
        mock_context: dict[str, request.Request],
    ) -> None:
        nested_data = {"messages": {"user": {"profile": ["Invalid profile data"]}}}
        exception = exceptions.ValidationError(nested_data)

        response = custom_exception_handler(exception, mock_context)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_data["messages"]["user"]["profile"] == ["Invalid profile data"]

    def test_token_validation_error_in_docstring(
        self,
        mock_context: dict[str, request.Request],
    ) -> None:
        token_error_data = {
            "messages": [
                {
                    "token_class": "AccessToken",
                    "token_type": "access",
                    "message": "Token is invalid or expired",
                }
            ]
        }
        exception = exceptions.AuthenticationFailed(token_error_data)

        response = custom_exception_handler(exception, mock_context)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data["status_code"] == status.HTTP_401_UNAUTHORIZED
        assert response_data["code"] == "authentication_failed"
        assert len(response_data["messages"]) == 1
        assert response_data["messages"][0]["token_class"] == "AccessToken"  # noqa: S105
