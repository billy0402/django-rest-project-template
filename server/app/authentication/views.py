from ninja_extra import api_controller, http_post
from ninja_jwt import controller as jwt_controller
from ninja_jwt.controller import schema as jwt_schema

from server.app.authentication import schema as auth_schema


@api_controller("/auth", tags=["auth"])
class AuthTokenController(jwt_controller.NinjaJWTDefaultController):  # pyright: ignore[reportGeneralTypeIssues]
    """custom path prefix."""

    @http_post(
        "/obtain",
        response=auth_schema.TokenObtainPairOutputSchema,
        url_name="token_obtain_pair",
        operation_id="token_obtain_pair",
    )
    def obtain_token(
        self,
        user_token: jwt_schema.obtain_pair_schema,  # pyright: ignore[reportInvalidTypeForm]
    ) -> auth_schema.TokenObtainPairOutputSchema:
        return super().obtain_token(user_token)
