from django.contrib import auth
from rest_framework import serializers

User = auth.get_user_model()


class EditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class BaseSerializer(serializers.ModelSerializer):
    creator = EditorSerializer(read_only=True)
    editor = EditorSerializer(read_only=True)
