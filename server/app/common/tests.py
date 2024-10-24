import pytest
from rest_framework import status, test

from server.app.common import views as common_views


@pytest.fixture
def factory() -> test.APIRequestFactory:
    return test.APIRequestFactory()


def test_health(factory: test.APIRequestFactory) -> None:
    request = factory.get("/api/v1/_/health")
    response = common_views.health(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": True}


def test_version(factory: test.APIRequestFactory) -> None:
    request = factory.get("/api/v1/_/version")
    response = common_views.version(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"version": 1}
