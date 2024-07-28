from ninja_extra import ControllerBase, api_controller, http_post
from ninja_jwt import controller as jwt_contollers

from server.app.authentication import schema as auth_schema


@api_controller("/auth", tags=["auth"])
class AuthTokenController(
    jwt_contollers.TokenVerificationController,
    jwt_contollers.TokenObtainPairController,
    ControllerBase,
):
    @http_post(
        "/obtain",
        response=auth_schema.TokenObtainOutputSchema,
        url_name="token_obtain",
        operation_id="token_obtain",
    )
    def obtain_token(
        self,
        user_token: auth_schema.TokenObtainInputSchema,
    ) -> auth_schema.TokenObtainOutputSchema:
        return super().obtain_token(user_token)
