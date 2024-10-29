import datetime

import pytest
from django import http
from django.contrib import admin
from django.utils import timezone
from model_bakery import baker

from server.app.authentication import models as auth_models
from server.utils.django import admin as util_admin
from server.utils.django.tests import models as test_models


@pytest.fixture
def admin_user() -> auth_models.User:
    return baker.make(
        auth_models.User,
        username="admin",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def mock_request(admin_user: auth_models.User) -> http.HttpRequest:
    request = http.HttpRequest()
    request.user = admin_user
    return request


class TestBaseAdmin:
    def test_readonly_fields(self) -> None:
        base_admin = util_admin.BaseAdmin(
            model=test_models.MockModel,
            admin_site=admin.site,
        )
        assert "created_by" in base_admin.readonly_fields
        assert "updated_by" in base_admin.readonly_fields

    @pytest.mark.django_db
    def test_save_model_on_create(
        self,
        mock_request: http.HttpRequest,
        admin_user: auth_models.User,
    ) -> None:
        base_admin = util_admin.BaseAdmin(
            model=test_models.MockModel,
            admin_site=admin.site,
        )
        obj = test_models.MockModel()
        form = base_admin.get_form(mock_request)(obj)

        base_admin.save_model(mock_request, obj, form, change=False)

        assert obj.created_by == admin_user
        assert obj.updated_by == admin_user

    @pytest.mark.django_db
    def test_save_model_on_update(
        self,
        mock_request: http.HttpRequest,
        admin_user: auth_models.User,
    ) -> None:
        base_admin = util_admin.BaseAdmin(
            model=test_models.MockModel,
            admin_site=admin.site,
        )
        created_user = baker.make(auth_models.User)
        obj = baker.make(
            test_models.MockModel,
            created_by=created_user,
            updated_by=created_user,
        )
        form = base_admin.get_form(mock_request)(obj)

        base_admin.save_model(mock_request, obj, form, change=True)

        assert obj.created_by == created_user
        assert obj.updated_by == admin_user


@pytest.mark.django_db
class TestSoftDeletableAdmin:
    @pytest.mark.parametrize(
        ("deleted_at", "expected"),
        [(timezone.now(), True), (None, False)],
    )
    def test_is_deleted(
        self,
        deleted_at: datetime.datetime | None,
        expected: bool,  # noqa: FBT001
    ) -> None:
        soft_admin = util_admin.SoftDeletableAdmin(
            model=test_models.MockSoftDeletableModel,
            admin_site=admin.site,
        )
        obj = baker.make(test_models.MockSoftDeletableModel, deleted_at=deleted_at)

        assert soft_admin.is_deleted(obj) is expected

    def test_get_list_display(self, mock_request: http.HttpRequest) -> None:
        soft_admin = util_admin.SoftDeletableAdmin(
            model=test_models.MockSoftDeletableModel,
            admin_site=admin.site,
        )
        soft_admin.list_display = ("id", "name")

        list_display = soft_admin.get_list_display(mock_request)

        assert list(list_display) == ["id", "name", "is_deleted"]

    def test_get_queryset_includes_deleted(
        self,
        mock_request: http.HttpRequest,
    ) -> None:
        soft_admin = util_admin.SoftDeletableAdmin(
            model=test_models.MockSoftDeletableModel,
            admin_site=admin.site,
        )
        active = baker.make(test_models.MockSoftDeletableModel, name="active")
        deleted = baker.make(
            test_models.MockSoftDeletableModel,
            name="deleted",
            deleted_at=timezone.now(),
        )

        qs = soft_admin.get_queryset(mock_request)

        assert len(qs) == 2  # noqa: PLR2004
        assert list(qs.order_by("name")) == [active, deleted]

    def test_get_queryset_respects_ordering(
        self,
        mock_request: http.HttpRequest,
    ) -> None:
        soft_admin = util_admin.SoftDeletableAdmin(
            model=test_models.MockSoftDeletableModel,
            admin_site=admin.site,
        )
        soft_admin.ordering = ("name",)
        obj1 = baker.make(test_models.MockSoftDeletableModel, name="obj1")
        obj2 = baker.make(test_models.MockSoftDeletableModel, name="obj2")

        queryset = soft_admin.get_queryset(mock_request)

        assert list(queryset) == [obj1, obj2]


@pytest.mark.django_db
class TestDeleteSelected:
    def test_delete_selected_marks_as_deleted(
        self,
        mock_request: http.HttpRequest,
    ) -> None:
        soft_admin = util_admin.SoftDeletableAdmin(
            model=test_models.MockSoftDeletableModel,
            admin_site=admin.site,
        )
        obj1 = baker.make(test_models.MockSoftDeletableModel)
        obj2 = baker.make(test_models.MockSoftDeletableModel)
        qs = test_models.MockSoftDeletableModel.objects.all()

        util_admin.delete_selected(soft_admin, mock_request, qs)  # pyright: ignore[reportArgumentType]

        obj1.refresh_from_db()
        obj2.refresh_from_db()
        assert obj1.deleted_at is not None
        assert obj2.deleted_at is not None
