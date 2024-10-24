from rest_framework import request

from server.app.authentication import models as auth_models


class AuthenticatedRequest(request.Request):
    @property
    def user(self) -> auth_models.User:
        return super().user  # pyright: ignore[reportReturnType]

    @user.setter
    def user(self, value: auth_models.User) -> None:
        super().user = value
