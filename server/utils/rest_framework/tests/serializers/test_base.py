import pytest
from model_bakery import baker
from rest_framework import request as drf_request
from rest_framework import test

from server.app.authentication import models as auth_models
from server.utils.django.tests import models as test_models
from server.utils.rest_framework import fields as util_fields
from server.utils.rest_framework.serializers import base as base_serializers


class MockSerializer(base_serializers.BaseSerializer):
    class Meta:
        model = test_models.MockModel
        fields = base_serializers.base_model_fields


@pytest.fixture
def factory() -> test.APIRequestFactory:
    return test.APIRequestFactory()


@pytest.fixture
def user() -> auth_models.User:
    return baker.make(
        auth_models.User,
        username="testuser",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def mock_request(
    factory: test.APIRequestFactory,
    user: auth_models.User,
) -> drf_request.Request:
    request = factory.get("/")
    request = drf_request.Request(request)
    request.user = user
    return request


class TestUserActionLogSerializer:
    def test_fields(self) -> None:
        serializer = base_serializers.UserActionLogSerializer()
        assert set(serializer.Meta.fields) == {
            "id",
            "username",
            "first_name",
            "last_name",
        }

    @pytest.mark.django_db
    def test_serialization(self, user: auth_models.User) -> None:
        serializer = base_serializers.UserActionLogSerializer(user)
        data = serializer.data

        assert "id" in data
        assert data["username"] == "testuser"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"


class TestBaseSerializer:
    def test_created_by_field(self) -> None:
        serializer = MockSerializer()
        field = serializer.fields["created_by"]

        assert isinstance(field, base_serializers.UserActionLogSerializer)
        assert field.read_only is True
        assert isinstance(field.default, util_fields.CurrentUserDefault)

    def test_updated_by_field(self) -> None:
        serializer = MockSerializer()
        field = serializer.fields["updated_by"]

        assert isinstance(field, base_serializers.UserActionLogSerializer)
        assert field.read_only is True
        assert isinstance(field.default, util_fields.CurrentUserDefault)

    @pytest.mark.django_db
    def test_create_with_user(
        self,
        mock_request: drf_request.Request,
        user: auth_models.User,
    ) -> None:
        serializer = MockSerializer(data={}, context={"request": mock_request})
        serializer.is_valid()

        assert serializer.data["created_by"]["username"] == str(user.username)
        assert serializer.data["updated_by"]["username"] == str(user.username)

    @pytest.mark.django_db
    def test_update_with_user(
        self,
        mock_request: drf_request.Request,
        user: auth_models.User,
    ) -> None:
        created_user = baker.make(
            auth_models.User,
            username="createduser",
            first_name="Created",
            last_name="User",
        )
        obj = baker.make(
            test_models.MockModel,
            created_by=created_user,
            updated_by=created_user,
        )

        serializer = MockSerializer(
            instance=obj,
            data={},
            context={"request": mock_request},
        )
        serializer.is_valid()
        serializer.save(updated_by=user)

        assert serializer.data["created_by"]["username"] == str(created_user.username)
        assert serializer.data["updated_by"]["username"] == str(user.username)


class TestBaseModelFields:
    def test_base_model_fields(self) -> None:
        expected_fields = ("id", "created_at", "updated_at", "created_by", "updated_by")
        assert set(base_serializers.base_model_fields) == set(expected_fields)
