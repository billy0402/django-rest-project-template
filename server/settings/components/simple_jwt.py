import datetime

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "TOKEN_OBTAIN_SERIALIZER": "server.app.authentication.serializers.MyTokenObtainPairSerializer",  # noqa: E501
    "UPDATE_LAST_LOGIN": True,
}
