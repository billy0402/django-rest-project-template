import pytest
from django.utils import timezone
from model_bakery import baker

from server.utils.django import managers as util_managers
from server.utils.django.tests import models as test_models


@pytest.fixture
def test_objects() -> dict[str, test_models.MockSoftDeletableModel]:
    active1 = baker.make(test_models.MockSoftDeletableModel, name="active1")
    active2 = baker.make(test_models.MockSoftDeletableModel, name="active2")
    deleted = baker.make(
        test_models.MockSoftDeletableModel,
        name="deleted",
        deleted_at=timezone.now(),
    )
    return {"active1": active1, "active2": active2, "deleted": deleted}


@pytest.mark.django_db
class TestSoftDeletableQuerySet:
    @pytest.mark.usefixtures("test_objects")
    def test_delete_set_deleted_at(self) -> None:
        queryset = test_models.MockSoftDeletableModel.objects.filter(name="active1")
        queryset.delete()

        obj = test_models.MockSoftDeletableModel.all_objects.get(name="active1")
        assert isinstance(obj.deleted_at, timezone.datetime)

    @pytest.mark.usefixtures("test_objects")
    def test_undelete_clear_deleted_at(self) -> None:
        queryset = test_models.MockSoftDeletableModel.all_objects.filter(name="deleted")
        queryset.undelete()  # pyright: ignore[reportAttributeAccessIssue]

        obj = test_models.MockSoftDeletableModel.objects.get(name="deleted")
        assert obj.deleted_at is None

    @pytest.mark.usefixtures("test_objects")
    def test_bulk_delete(self) -> None:
        queryset = test_models.MockSoftDeletableModel.objects.all()
        queryset.delete()

        all_qs = test_models.MockSoftDeletableModel.all_objects.all()

        assert all(isinstance(obj.deleted_at, timezone.datetime) for obj in all_qs)

    @pytest.mark.usefixtures("test_objects")
    def test_bulk_undelete(self) -> None:
        test_models.MockSoftDeletableModel.objects.all().delete()

        all_qs = test_models.MockSoftDeletableModel.all_objects.all()
        all_qs.undelete()  # pyright: ignore[reportAttributeAccessIssue]

        assert all(obj.deleted_at is None for obj in all_qs)


class TestSoftDeletableManager:
    @pytest.mark.django_db
    @pytest.mark.usefixtures("test_objects")
    def test_get_queryset_excludes_deleted(self) -> None:
        queryset = test_models.MockSoftDeletableModel.objects.all()

        assert len(queryset) == 2  # noqa: PLR2004
        names = sorted(obj.name for obj in queryset)
        assert names == ["active1", "active2"]

    @pytest.mark.django_db
    @pytest.mark.usefixtures("test_objects")
    def test_get_queryset_includes_deleted_with_base_manager(self) -> None:
        base_qs = test_models.MockSoftDeletableModel.all_objects.all()

        assert len(base_qs) == 3  # noqa: PLR2004
        names = sorted(obj.name for obj in base_qs)
        assert names == ["active1", "active2", "deleted"]

    def test_queryset_class(self) -> None:
        assert isinstance(
            test_models.MockSoftDeletableModel.objects.all(),
            util_managers.SoftDeletableQuerySet,
        )


@pytest.mark.django_db
class TestGlobalQuerySet:
    @pytest.mark.usefixtures("test_objects")
    def test_undelete_clear_deleted_at(self) -> None:
        queryset = test_models.MockSoftDeletableModel.all_objects.filter(name="deleted")
        queryset.undelete()  # pyright: ignore[reportAttributeAccessIssue]

        obj = test_models.MockSoftDeletableModel.objects.get(name="deleted")
        assert obj.deleted_at is None

    @pytest.mark.usefixtures("test_objects")
    def test_bulk_undelete(self) -> None:
        test_models.MockSoftDeletableModel.objects.all().delete()

        all_qs = test_models.MockSoftDeletableModel.all_objects.all()
        all_qs.undelete()  # pyright: ignore[reportAttributeAccessIssue]

        assert all(obj.deleted_at is None for obj in all_qs)


@pytest.mark.django_db
class TestGlobalManager:
    @pytest.mark.usefixtures("test_objects")
    def test_get_queryset_includes_all_objects(self) -> None:
        queryset = test_models.MockSoftDeletableModel.all_objects.all()

        assert len(queryset) == 3  # noqa: PLR2004
        names = sorted(obj.name for obj in queryset)
        assert names == ["active1", "active2", "deleted"]

    def test_queryset_class(self) -> None:
        assert isinstance(
            test_models.MockSoftDeletableModel.all_objects.all(),
            util_managers.GlobalQuerySet,
        )

    @pytest.mark.usefixtures("test_objects")
    def test_filter_includes_deleted(self) -> None:
        queryset = test_models.MockSoftDeletableModel.all_objects.filter(
            deleted_at__isnull=False
        )

        assert len(queryset) == 1
        assert queryset[0].name == "deleted"
