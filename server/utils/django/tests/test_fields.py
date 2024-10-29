import datetime
import uuid

import pytest
import time_machine
from django.utils import timezone
from model_bakery import baker

from server.utils.django import fields as util_fields
from server.utils.django.tests import models as test_models


class TestUUIDAutoField:
    def test_default_configuration(self) -> None:
        field = util_fields.UUIDAutoField()

        assert field.editable is False
        assert callable(field.default)
        assert isinstance(field.default(), uuid.UUID)

    def test_override_default(self) -> None:
        field = util_fields.UUIDAutoField(editable=True, default=uuid.uuid4)

        assert field.editable is True
        assert field.default == uuid.uuid4


class TestCreatedAtField:
    def test_default_configuration(self) -> None:
        field = util_fields.CreatedAtField()
        assert field.auto_now_add is True

    @pytest.mark.django_db
    @time_machine.travel("2024-01-01 12:00:00")
    def test_model_save(self) -> None:
        with time_machine.travel("2024-01-01 12:00:00"):
            model = test_models.MockModel()
            model.save()

        assert model.created_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )

        with time_machine.travel("2024-01-02 12:00:00"):
            model.save()

        assert model.created_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )


class TestUpdatedAtField:
    def test_default_configuration(self) -> None:
        field = util_fields.UpdatedAtField()
        assert field.auto_now is True

    @pytest.mark.django_db
    def test_model_save(self) -> None:
        with time_machine.travel("2024-01-01 12:00:00"):
            model = test_models.MockModel()
            model.save()

        assert model.updated_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )
        assert model.updated_at == model.created_at

        with time_machine.travel("2024-01-02 12:00:00"):
            model.save()

        assert model.updated_at == timezone.datetime(
            2024, 1, 2, 12, 0, tzinfo=datetime.UTC
        )
        assert model.updated_at != model.created_at

    @pytest.mark.django_db
    def test_pre_save_copied_created_at(self) -> None:
        model = test_models.MockModel()
        model.save()

        assert model.updated_at == model.created_at

    @pytest.mark.django_db
    def test_pre_save_without_created_at(self) -> None:
        model = test_models.ModelWithoutCreatedAt()

        with time_machine.travel("2024-01-01 12:00:00"):
            model.save()

        assert model.updated_at == timezone.datetime(
            2024, 1, 1, 12, 0, tzinfo=datetime.UTC
        )


@pytest.mark.django_db
class TestFieldsIntegration:
    def test_full_model_lifecycle(self) -> None:
        model = baker.make(test_models.MockModel)

        assert isinstance(model.id, uuid.UUID)
        assert model.created_at == model.updated_at
        initial_created_at = model.created_at
        initial_updated_at = model.updated_at

        new_time = initial_updated_at + datetime.timedelta(seconds=1)
        with time_machine.travel(new_time):
            model.save()

        assert model.created_at == initial_created_at
        assert model.updated_at == new_time
        assert model.updated_at > model.created_at
