from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from server.app.common.views import health, version


class TestCommonAPI(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_health(self) -> None:
        request = self.factory.get("/api/v1/_/health", {"status": True})
        response = health(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": True})

    def test_version(self) -> None:
        request = self.factory.get("/api/v1/_/health", {"status": True})
        response = version(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"version": 1})
