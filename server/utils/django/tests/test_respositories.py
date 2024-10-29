import pytest
from django.db import models
from model_bakery import baker

from server.utils.django import repositories as util_repositories
from server.utils.django.tests import models as test_models


class MockRepository(util_repositories.BaseRepository[test_models.MockModel]):
    model = test_models.MockModel
    queryset = test_models.MockModel.objects.all()


@pytest.fixture
def mock_repository() -> MockRepository:
    return MockRepository()


@pytest.fixture
def mock_instance() -> test_models.MockModel:
    return baker.make(test_models.MockModel)


class TestBaseRepository:
    def test_repository_has_model_class(self, mock_repository: MockRepository) -> None:
        assert mock_repository.model == test_models.MockModel
        assert issubclass(mock_repository.model, models.Model)

    def test_repository_has_queryset(self, mock_repository: MockRepository) -> None:
        assert isinstance(mock_repository.queryset, models.QuerySet)
        assert mock_repository.queryset.model == test_models.MockModel

    def test_repository_model_generic_type_checking(self) -> None:
        def use_repository(
            repo: util_repositories.BaseRepository[test_models.MockModel],
        ) -> None:
            assert repo.model == test_models.MockModel

        repo = MockRepository()
        use_repository(repo)

    @pytest.mark.django_db
    def test_repository_with_db(
        self,
        mock_repository: MockRepository,
        mock_instance: test_models.MockModel,
    ) -> None:
        first_obj = mock_repository.queryset.first()
        assert first_obj == mock_instance

    @pytest.mark.django_db
    def test_repository_queryset_filtering(self) -> None:
        test_models.MockModel.objects.create(name="first")
        test_models.MockModel.objects.create(name="second")

        repo = MockRepository()
        filtered_qs = repo.queryset.filter(name="first")
        first_obj = filtered_qs.first()

        assert filtered_qs.count() == 1
        assert first_obj is not None
        assert first_obj.name == "first"

    def test_cannot_instantiate_base_repository(self) -> None:
        with pytest.raises(TypeError):
            util_repositories.BaseRepository()
