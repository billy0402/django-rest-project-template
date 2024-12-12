from rest_framework import serializers

from server.app.authentication import models as auth_models
from server.utils.rest_framework import fields as util_fields


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
    created_by = UserActionLogSerializer(
        default=util_fields.CurrentUserDefault(),
        read_only=True,
    )
    updated_by = UserActionLogSerializer(
        default=util_fields.CurrentUserDefault(),
        read_only=True,
    )


uuid_primary_key_fields = ("id",)
timestamp_fields = ("created_at", "updated_at")
user_action_log_fields = ("created_by", "updated_by")
base_model_fields = uuid_primary_key_fields + timestamp_fields + user_action_log_fields
