from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "server.utils.django.fields.UUIDAutoField"
    name = "server.app.common"
