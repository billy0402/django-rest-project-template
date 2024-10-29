import datetime
import uuid

import pytest
import time_machine
from django.utils import timezone
from model_bakery import baker

from server.app.authentication import models as auth_models
from server.utils.django.tests import models as test_models


@pytest.mark.django_db
class TestUUIDModel:
    def test_id_is_uuid(self) -> None:
        obj = baker.make(test_models.MockModel)
        assert isinstance(obj.id, uuid.UUID)


@pytest.mark.django_db
class TestTimestampModel:
    def test_set_timestamp_on_create(self) -> None:
        with time_machine.travel("2024-01-01 12:00:00"):
            obj = baker.make(test_models.MockModel)

        assert obj.created_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )
        assert obj.updated_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )

    def test_update_updated_at_on_update(self) -> None:
        with time_machine.travel("2024-01-01 12:00:00"):
            obj = baker.make(test_models.MockModel)

        with time_machine.travel("2024-01-02 12:00:00"):
            obj.save()
            obj.refresh_from_db()

        assert obj.created_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )
        assert obj.updated_at == timezone.datetime(
            2024, 1, 2, 12, 0, tzinfo=datetime.UTC
        )


@pytest.mark.django_db
class TestUserActionLogModel:
    def test_created_by_nullable(self) -> None:
        obj = baker.make(test_models.MockModel, created_by=None)
        assert obj.created_by is None

    def test_updated_by_nullable(self) -> None:
        obj = baker.make(test_models.MockModel, updated_by=None)
        assert obj.updated_by is None

    def test_user_relationships(self) -> None:
        user = baker.make(auth_models.User)
        obj = baker.make(test_models.MockModel, created_by=user, updated_by=user)

        assert obj.created_by == user
        assert obj.updated_by == user
        # Test reverse relationships
        assert obj in user.tests_mockmodel_created_by.all()  # pyright: ignore[reportAttributeAccessIssue]
        assert obj in user.tests_mockmodel_updated_by.all()  # pyright: ignore[reportAttributeAccessIssue]


@pytest.mark.django_db
class TestBaseModel:
    def test_ordering(self) -> None:
        with time_machine.travel("2024-01-01 12:00:00"):
            obj1 = baker.make(test_models.MockModel)
        with time_machine.travel("2024-01-02 12:00:00"):
            obj2 = baker.make(test_models.MockModel)

        qs = list(test_models.MockModel.objects.all())
        assert qs == [obj2, obj1]


@pytest.mark.django_db
class TestSoftDeletableModel:
    @time_machine.travel("2024-01-01 12:00:00")
    def test_soft_delete(self) -> None:
        obj = baker.make(test_models.MockSoftDeletableModel)

        obj.delete()
        obj.refresh_from_db()

        assert obj.deleted_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )

    def test_hard_delete(self) -> None:
        obj = baker.make(test_models.MockSoftDeletableModel)
        obj_id: int = obj.id  # pyright: ignore[reportAttributeAccessIssue]

        obj.delete(soft=False)

        with pytest.raises(test_models.MockSoftDeletableModel.DoesNotExist):
            test_models.MockSoftDeletableModel.objects.get(id=obj_id)

    def test_delete_return_values(self) -> None:
        obj = baker.make(test_models.MockSoftDeletableModel)
        obj2 = baker.make(test_models.MockSoftDeletableModel)

        # Test soft delete return
        result = obj.delete()
        assert result == (0, {})

        # Test hard delete return
        count, result = obj2.delete(soft=False)
        assert count > 0
        assert isinstance(result, dict)

    def test_undelete(self) -> None:
        obj = baker.make(test_models.MockSoftDeletableModel)
        obj.delete()

        obj.undelete()
        obj.refresh_from_db()

        assert obj.deleted_at is None

    def test_objects_manager_excludes_deleted(self) -> None:
        active = baker.make(test_models.MockSoftDeletableModel)
        deleted = baker.make(test_models.MockSoftDeletableModel)
        deleted.delete()

        objects = list(test_models.MockSoftDeletableModel.objects.all())
        assert objects == [active]

    def test_all_objects_manager_includes_deleted(self) -> None:
        active = baker.make(test_models.MockSoftDeletableModel)
        deleted = baker.make(test_models.MockSoftDeletableModel)
        deleted.delete()

        objects = list(test_models.MockSoftDeletableModel.all_objects.all())
        assert objects == [active, deleted]
