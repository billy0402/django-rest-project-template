import pytest
from ninja import testing as ninja_test
from ninja_extra import status

from server.app.common.views import router as common_router


@pytest.fixture
def factory() -> ninja_test.TestClient:
    return ninja_test.TestClient(common_router)


class TestCommonViews:
    def test_health(self, factory: ninja_test.TestClient) -> None:
        response = factory.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"status": True}

    def test_version(self, factory: ninja_test.TestClient) -> None:
        response = factory.get("/version")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"version": 1}
