import typing as t

import pytest
from model_bakery import baker
from rest_framework import mixins, status, test, views

from server.app.authentication import models as auth_models
from server.utils.django.tests import models as test_models
from server.utils.rest_framework import viewsets as util_viewsets
from server.utils.rest_framework.serializers import base as base_serializers


class MockSerializer(base_serializers.BaseSerializer):
    class Meta:
        model = test_models.MockModel
        fields = ("id", "name")


class MockBaseModelSerializer(base_serializers.BaseSerializer):
    class Meta:
        model = test_models.MockModel
        fields = (*base_serializers.base_model_fields, "name")


@pytest.fixture
def factory() -> test.APIRequestFactory:
    return test.APIRequestFactory()


@pytest.fixture
def user() -> auth_models.User:
    return baker.make(auth_models.User)


@pytest.fixture
def mock_instance(user: auth_models.User) -> test_models.MockModel:
    return baker.make(test_models.MockModel, created_by=user, updated_by=user)


ViewSetFactory = t.Callable[
    [type[base_serializers.BaseSerializer], dict[str, str] | None], t.Any
]


@pytest.fixture
def viewset_factory() -> ViewSetFactory:
    def _create_viewset(
        serializer_class: type[base_serializers.BaseSerializer],
        actions: dict[str, t.Any] | None = None,
    ) -> ViewSetFactory:
        class MockViewSet(
            mixins.ListModelMixin,
            mixins.RetrieveModelMixin,
            util_viewsets.BaseGenericViewSet,
        ):
            queryset = test_models.MockModel.objects.all()

            def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
                super().__init__(*args, **kwargs)
                self.serializer_class = serializer_class

        return MockViewSet.as_view(actions=actions)

    return _create_viewset


ModelViewSetFactory = t.Callable[[type[base_serializers.BaseSerializer]], t.Any]


@pytest.fixture
def model_viewset_factory() -> ModelViewSetFactory:
    def _create_viewset(
        serializer_class: type[base_serializers.BaseSerializer],
    ) -> ModelViewSetFactory:
        class MockModelViewSet(util_viewsets.BaseModelViewSet):
            queryset = test_models.MockModel.objects.all()

            def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
                super().__init__(*args, **kwargs)
                self.serializer_class = serializer_class

        return MockModelViewSet.as_view(
            {"get": "retrieve", "post": "create", "put": "update"},
        )

    return _create_viewset


@pytest.mark.django_db
class TestUserActionLogMixins:
    def test_create_user_action_log(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
    ) -> None:
        request = factory.post("/items", {"name": "Test Example"})
        test.force_authenticate(request, user=user)

        view = util_viewsets.CreateUserActionLogMixin()
        view.request = views.APIView().initialize_request(request)

        serializer = MockBaseModelSerializer(data={"name": "Test Example"})
        serializer.is_valid(raise_exception=True)
        view.perform_create(serializer)

        assert serializer.instance.created_by == user
        assert serializer.instance.updated_by == user

    def test_update_user_action_log(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
        mock_instance: test_models.MockModel,
    ) -> None:
        request = factory.put("/items/1", {"name": "Updated"})
        test.force_authenticate(request, user=user)

        view = util_viewsets.UpdateUserActionLogMixin()
        view.request = views.APIView().initialize_request(request)

        serializer = MockBaseModelSerializer(mock_instance, data={"name": "Updated"})
        serializer.is_valid(raise_exception=True)
        view.perform_update(serializer)

        assert serializer.instance.created_by == user
        assert serializer.instance.updated_by == user


@pytest.mark.django_db
class TestBaseGenericViewSet:
    @pytest.mark.usefixtures("mock_instance")
    def test_list_without_user_fields(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
        viewset_factory: ViewSetFactory,
    ) -> None:
        request = factory.get("/items")
        test.force_authenticate(request, user=user)

        view = viewset_factory(MockSerializer, {"get": "list"})
        response = view(request)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_200_OK
        results = response_data["results"]
        assert "created_by" not in results[0]
        assert "updated_by" not in results[0]

    @pytest.mark.usefixtures("mock_instance")
    def test_list_with_user_fields(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
        viewset_factory: ViewSetFactory,
    ) -> None:
        request = factory.get("/items")
        test.force_authenticate(request, user=user)

        view = viewset_factory(MockBaseModelSerializer, {"get": "list"})
        response = view(request)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_200_OK
        results = response_data["results"]
        assert "created_by" in results[0]
        assert "updated_by" in results[0]

    def test_retrieve_with_user_fields(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
        mock_instance: test_models.MockModel,
        viewset_factory: ViewSetFactory,
    ) -> None:
        request = factory.get(f"/items/{mock_instance.id}")
        test.force_authenticate(request, user=user)

        view = viewset_factory(MockBaseModelSerializer, {"get": "retrieve"})
        response = view(request, pk=mock_instance.id)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_200_OK
        assert response_data["created_by"]["id"] == str(user.id)
        assert response_data["updated_by"]["id"] == str(user.id)


@pytest.mark.django_db
class TestBaseModelViewSet:
    def test_retrieve_with_user_fields(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
        mock_instance: test_models.MockModel,
        model_viewset_factory: ModelViewSetFactory,
    ) -> None:
        request = factory.get(f"/items/{mock_instance.id}")
        test.force_authenticate(request, user=user)

        view = model_viewset_factory(MockBaseModelSerializer)
        response = view(request, pk=mock_instance.id)
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response.status_code == status.HTTP_200_OK
        assert mock_instance.created_by is not None
        assert response_data["created_by"]["id"] == str(mock_instance.created_by.id)
        assert mock_instance.updated_by is not None
        assert response_data["updated_by"]["id"] == str(mock_instance.updated_by.id)

    def test_create_with_user_fields(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
        model_viewset_factory: ModelViewSetFactory,
    ) -> None:
        request = factory.post("/items", {"name": "Test Item"})
        test.force_authenticate(request, user=user)

        view = model_viewset_factory(MockBaseModelSerializer)
        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED
        created_item = test_models.MockModel.objects.get(name="Test Item")
        assert created_item.created_by == user
        assert created_item.updated_by == user

    def test_update_with_user_fields(
        self,
        factory: test.APIRequestFactory,
        user: auth_models.User,
        mock_instance: test_models.MockModel,
        model_viewset_factory: ModelViewSetFactory,
    ) -> None:
        request = factory.put(
            f"/items/{mock_instance.id}",
            {"name": "Updated Item"},
            format="json",
        )
        test.force_authenticate(request, user=user)

        view = model_viewset_factory(MockBaseModelSerializer)
        response = view(request, pk=mock_instance.id)

        assert response.status_code == status.HTTP_200_OK
        mock_instance.refresh_from_db()
        assert mock_instance.name == "Updated Item"
        assert mock_instance.created_by == mock_instance.created_by
        assert mock_instance.updated_by == user

    def test_unauthorized_access(
        self,
        factory: test.APIRequestFactory,
        model_viewset_factory: ModelViewSetFactory,
    ) -> None:
        request = factory.post("/items", {"name": "Test Item"})
        view = model_viewset_factory(MockBaseModelSerializer)
        response = view(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
