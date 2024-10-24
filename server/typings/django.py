from django import http

from server.app.authentication import models as auth_models


class AuthenticatedHttpRequest(http.HttpRequest):
    user: auth_models.User
