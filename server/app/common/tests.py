from django import test
from rest_framework import status
from rest_framework import test as rest_test

from server.app.common import views as common_views


class TestCommonAPI(test.TestCase):
    def setUp(self) -> None:
        self.factory = rest_test.APIRequestFactory()

    def test_health(self) -> None:
        request = self.factory.get("/api/v1/_/health", {"status": True})
        response = common_views.health(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": True})

    def test_version(self) -> None:
        request = self.factory.get("/api/v1/_/health", {"status": True})
        response = common_views.version(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"version": 1})
