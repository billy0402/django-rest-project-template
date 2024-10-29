from rest_framework import fields


class CurrentUserDefault(fields.CurrentUserDefault):
    def __call__(self, serializer_field: fields.Field) -> None:
        if serializer_field.context.get("request", None) is None:
            return None
        return serializer_field.context["request"].user
