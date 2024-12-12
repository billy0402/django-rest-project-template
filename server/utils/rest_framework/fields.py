from rest_framework import fields


class CurrentUserDefault(fields.CurrentUserDefault):
    def __call__(self, serializer_field: fields.Field) -> None:
        request = serializer_field.context.get("request", None)
        if request is None:
            return None
        return request.user
