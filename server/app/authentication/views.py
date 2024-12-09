from ninja_extra import ControllerBase, api_controller, http_post
from ninja_jwt import controller as jwt_contollers
from ninja_jwt import schema as jwt_schema


@api_controller("/auth", tags=["auth"])
class AuthTokenController(
    jwt_contollers.TokenVerificationController,
    jwt_contollers.TokenObtainPairController,
    ControllerBase,
):
    """custom path prefix."""

    @http_post(
        "/obtain",
        response=jwt_schema.TokenObtainPairOutputSchema,
        url_name="token_obtain",
        operation_id="token_obtain",
    )
    def obtain_token(
        self,
        user_token: jwt_schema.TokenObtainPairInputSchema,
    ) -> jwt_schema.TokenObtainPairOutputSchema:
        return super().obtain_token(user_token)
