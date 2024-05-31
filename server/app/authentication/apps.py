from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "server.utils.django.fields.UUIDAutoField"
    name = "server.app.authentication"
