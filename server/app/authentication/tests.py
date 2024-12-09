import pytest
from model_bakery import baker
from ninja_extra import status
from ninja_extra import testing as ninja_test

from server.app.authentication import models as auth_models
from server.app.authentication import views as auth_views


@pytest.fixture
def client() -> ninja_test.TestClient:
    return ninja_test.TestClient(auth_views.AuthTokenController)


@pytest.fixture
def user() -> auth_models.User:
    return baker.make(auth_models.User, username="user", password="password")  # noqa: S106


@pytest.mark.django_db
class TestCommonViews:
    def test_obtain(
        self,
        client: ninja_test.TestClient,
        user: auth_models.User,
    ) -> None:
        response = client.post(
            "/obtain",
            json={"username": user.username, "password": user.password},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["access"] is not None
        assert response.json()["refresh"] is not None

    def test_version(self, client: ninja_test.TestClient) -> None:
        response = client.get("/version")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"version": 1}
