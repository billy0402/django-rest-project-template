import pytest
from model_bakery import baker
from rest_framework import request as drf_request
from rest_framework import serializers, test

from server.app.authentication import models as auth_models
from server.utils.rest_framework import fields as util_fields


class MockSerializer(serializers.Serializer):
    user = serializers.CharField(default=util_fields.CurrentUserDefault())


@pytest.fixture
def factory() -> test.APIRequestFactory:
    return test.APIRequestFactory()


@pytest.fixture
def mock_request(factory: test.APIRequestFactory) -> drf_request.Request:
    request = factory.get("/")
    user = baker.make(auth_models.User)
    request.user = user
    return request


@pytest.mark.django_db
class TestCurrentUserDefault:
    def test_current_user_default_with_request(
        self,
        mock_request: drf_request.Request,
    ) -> None:
        serializer = MockSerializer(context={"request": mock_request})
        assert serializer.fields["user"].get_default() == mock_request.user

    def test_current_user_default_without_request(self) -> None:
        serializer = MockSerializer()
        assert serializer.fields["user"].get_default() is None
