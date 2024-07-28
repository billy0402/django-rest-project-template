import typing as t

from ninja import schema
from ninja_jwt import schema as jwt_schema
from ninja_jwt import tokens as jwt_tokens

from server.app.authentication import models as auth_models


class TokenObtainInputSchema(jwt_schema.TokenObtainPairInputSchema):
    @classmethod
    def get_token(cls, user: auth_models.User) -> dict:
        refresh = jwt_tokens.RefreshToken.for_user(user)
        refresh = t.cast(jwt_tokens.RefreshToken, refresh)
        refresh["username"] = user.username
        refresh["first_name"] = user.first_name
        refresh["last_name"] = user.last_name
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class TokenObtainOutputSchema(schema.Schema):
    access: str
    refresh: str
