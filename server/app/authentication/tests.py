import typing as t

import jwt
import pytest
from django.conf import settings
from ninja_extra import status
from ninja_extra import testing as ninja_test
from ninja_jwt import tokens as jwt_tokens

from server.app.authentication import models as auth_models
from server.app.authentication import views as auth_views


@pytest.fixture
def client() -> ninja_test.TestClient:
    return ninja_test.TestClient(auth_views.AuthTokenController)


@pytest.fixture
def user() -> auth_models.User:
    return auth_models.User.objects.create_user(  # pyright: ignore[reportAttributeAccessIssue]
        username="user",
        password="password",  # noqa: S106
    )


def decode_jwt(token: str) -> dict[str, t.Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


def asset_token(payload: dict[str, t.Any], user: auth_models.User) -> None:
    assert payload["user_id"] == str(user.id)
    assert payload["username"] == user.username
    assert payload["first_name"] == user.first_name
    assert payload["last_name"] == user.last_name


@pytest.mark.django_db
class TestCommonViews:
    def test_obtain(
        self,
        client: ninja_test.TestClient,
        user: auth_models.User,
    ) -> None:
        response = client.post(
            "/obtain",
            json={"username": user.username, "password": "password"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

        access_payload = decode_jwt(response.data["access"])
        asset_token(access_payload, user)
        refresh_payload = decode_jwt(response.data["refresh"])
        asset_token(refresh_payload, user)

    @pytest.mark.parametrize(
        "credentials",
        [
            {"username": "", "password": "testpassword"},  # Empty username
            {"username": "testuser", "password": ""},  # Empty password
            {"username": None, "password": None},  # None values
        ],
    )
    @pytest.mark.usefixtures("user")
    def test_obtain_with_invalid_input(
        self,
        client: ninja_test.TestClient,
        credentials: dict[str, str],
    ) -> None:
        response = client.post("/obtain", json=credentials)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_obtain_with_invalid_credentials(
        self,
        client: ninja_test.TestClient,
        user: auth_models.User,
    ) -> None:
        response = client.post(
            "/obtain",
            json={"username": user.username, "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data

    def test_obtain_with_inactive_user(
        self,
        client: ninja_test.TestClient,
        user: auth_models.User,
    ) -> None:
        user.is_active = False
        user.save()

        response = client.post(
            "/obtain",
            json={"username": user.username, "password": "password"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data

    def test_refresh(self, client: ninja_test.TestClient) -> None:
        refresh = jwt_tokens.RefreshToken()

        response = client.post("/refresh", json={"refresh": str(refresh)})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_refresh_with_invalid_input(self, client: ninja_test.TestClient) -> None:
        response = client.post("/refresh", json={})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_refresh_with_invalid_credentials(
        self,
        client: ninja_test.TestClient,
    ) -> None:
        response = client.post("/refresh", json={"refresh": "invalid_refresh"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data

    def test_verify(self, client: ninja_test.TestClient) -> None:
        token = jwt_tokens.RefreshToken()

        response = client.post("/verify", json={"token": str(token)})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {}

    def test_verify_with_invalid_token(self, client: ninja_test.TestClient) -> None:
        response = client.post("/verify", json={"token": "invalid_token"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data
