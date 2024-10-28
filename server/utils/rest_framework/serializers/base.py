from rest_framework import serializers

from server.app.authentication import models as auth_models


class UserActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.UserModel
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class BaseSerializer(serializers.ModelSerializer):
    created_by = UserActionLogSerializer(read_only=True)
    updated_by = UserActionLogSerializer(read_only=True)


uuid_model_fields = ("id",)
user_action_log_fields = ("created_by", "updated_by")
timestamp_fields = ("created_at", "updated_at")
base_model_fields = uuid_model_fields + user_action_log_fields + timestamp_fields
