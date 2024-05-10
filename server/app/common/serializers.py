from rest_framework import serializers


class HealthSerializer(serializers.Serializer):
    status = serializers.BooleanField(read_only=True)


class VersionSerializer(serializers.Serializer):
    version = serializers.IntegerField(read_only=True)
