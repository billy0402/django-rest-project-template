from django import test
from ninja import testing as ninja_test
from ninja_extra import status

from server.app.common.views import router as common_router


class TestCommonAPI(test.TestCase):
    def setUp(self) -> None:
        self.factory = ninja_test.TestClient(common_router)

    def test_health(self) -> None:
        response = self.factory.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": True})

    def test_version(self) -> None:
        response = self.factory.get("/version")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"version": 1})
