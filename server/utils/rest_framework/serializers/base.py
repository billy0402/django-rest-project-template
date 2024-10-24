from rest_framework import serializers

from server.app.authentication import models as auth_models


class EditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.UserModel
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class BaseSerializer(serializers.ModelSerializer):
    creator = EditorSerializer(read_only=True)
    editor = EditorSerializer(read_only=True)


uuid_model_fields = ("id",)
editor_model_fields = ("creator", "editor")
timestamp_model_fields = ("created_at", "updated_at")
base_model_fields = uuid_model_fields + editor_model_fields + timestamp_model_fields
