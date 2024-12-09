import typing as t
import uuid

import pytest
from model_bakery import baker
from ninja_extra import status
from ninja_extra import testing as ninja_test

from server.app.authentication import models as auth_models
from server.app.todo import models as todo_models
from server.app.todo import views as todo_views


@pytest.fixture
def client() -> ninja_test.TestClient:
    return ninja_test.TestClient(todo_views.TaskController)


class MockData(t.NamedTuple):
    user: auth_models.User
    categories: list[todo_models.Category]
    tags: list[todo_models.Tag]
    task: todo_models.Task


@pytest.fixture
def mock_data() -> MockData:
    user = baker.make(auth_models.User)
    tags = baker.make(todo_models.Tag, _quantity=3, _bulk_create=True)
    categories = baker.make(todo_models.Category, _quantity=3, _bulk_create=True)
    task = baker.make(
        todo_models.Task,
        tags=tags,
        category=categories[0],
        created_by=user,
        updated_by=user,
    )
    return MockData(user=user, categories=categories, tags=tags, task=task)


def assert_response(response_data: dict, expected_data: dict) -> None:
    assert isinstance(response_data["id"], str)
    assert response_data["title"] == expected_data["title"]
    assert response_data["description"] == expected_data["description"]
    assert response_data["is_finish"] == expected_data["is_finish"]
    assert all(tag in response_data["tags"] for tag in expected_data["tags"])
    assert response_data["category"] == expected_data["category"]
    assert response_data["attachment"] == expected_data["attachment"]
    assert response_data["end_at"] == expected_data["end_at"]

    assert isinstance(response_data["created_at"], str)
    assert isinstance(response_data["updated_at"], str)
    assert response_data["created_by"] == expected_data["created_by"]
    assert response_data["updated_by"] == expected_data["updated_by"]


@pytest.mark.django_db
class TestAuthorizationViewSet:
    def test_list(self, client: ninja_test.TestClient, mock_data: MockData) -> None:
        user, _, _, task = mock_data

        response = client.get("")
        first_item = response.data["results"][0]

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] > 0
        assert len(response.data["results"]) > 0
        expected_data = {
            "title": task.title,
            "description": task.description,
            "is_finish": task.is_finish,
            "tags": [{"id": str(tag.id), "name": tag.name} for tag in task.tags.all()],
            "category": {
                "id": str(task.category.id),
                "name": task.category.name,
            },
            "attachment": None,
            "end_at": task.end_at,
            "created_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "updated_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
        assert_response(first_item, expected_data)

    def test_list_empty(self, client: ninja_test.TestClient) -> None:
        response = client.get("")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0

    def test_detail(self, client: ninja_test.TestClient, mock_data: MockData) -> None:
        user, _, _, task = mock_data

        response = client.get(str(task.id))

        assert response.status_code == status.HTTP_200_OK
        expected_data = {
            "title": task.title,
            "description": task.description,
            "is_finish": task.is_finish,
            "tags": [{"id": str(tag.id), "name": tag.name} for tag in task.tags.all()],
            "category": {
                "id": str(task.category.id),
                "name": task.category.name,
            },
            "attachment": None,
            "end_at": task.end_at,
            "created_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "updated_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
        assert_response(response.data, expected_data)

    def test_retrieve_not_found(self, client: ninja_test.TestClient) -> None:
        response = client.get(str(uuid.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create(self, client: ninja_test.TestClient, mock_data: MockData) -> None:
        user, categories, tags, _ = mock_data

        category = categories[0]
        tag_ids = [str(tag.id) for tag in tags]
        data = {
            "title": "New Task",
            "description": "New Task Description",
            "is_finish": False,
            "category_id": str(category.id),
            "tag_ids": tag_ids,
            "attachment": None,
            "end_at": "2025-01-01T12:00:00Z",
        }
        response = client.post("", json=data, user=user)

        assert response.status_code == status.HTTP_201_CREATED
        expected_data = {
            "title": data["title"],
            "description": data["description"],
            "is_finish": data["is_finish"],
            "tags": [{"id": str(tag.id), "name": tag.name} for tag in tags],
            "category": {
                "id": str(category.id),
                "name": category.name,
            },
            "attachment": None,
            "end_at": data["end_at"],
            "created_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "updated_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
        assert_response(response.data, expected_data)
        assert response.data["created_at"] == response.data["updated_at"]
        assert response.data["created_by"] == response.data["updated_by"]

        assert todo_models.Task.objects.get(id=response.data["id"])

    def test_create_minimal(
        self,
        client: ninja_test.TestClient,
        mock_data: MockData,
    ) -> None:
        user, _, _, _ = mock_data

        data = {
            "title": "New Task",
        }
        response = client.post("", json=data, user=user)

        assert response.status_code == status.HTTP_201_CREATED
        expected_data = {
            "title": data["title"],
            "description": "",
            "is_finish": False,
            "tags": [],
            "category": None,
            "attachment": None,
            "end_at": None,
            "created_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "updated_by": {
                "id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
        assert_response(response.data, expected_data)

        assert todo_models.Task.objects.get(id=response.data["id"])

    @pytest.mark.skip("Not implemented")
    @pytest.mark.parametrize(
        ("invalid_values", "expected_error_fields"),
        [
            # Test case 1: Missing required fields
            ({"title": ""}, {"title"}),
            # Test case 2: Invalid category_id
            ({"category_id": str(uuid.uuid4())}, {"category_id"}),
            # Test case 3: Invalid tag_ids
            ({"tag_ids": [str(uuid.uuid4())]}, {"tag_ids"}),
            # Test case 4: Invalid date format
            ({"end_at": "invalid-date"}, {"end_at"}),
            # Test case 5: Multiple validation errors
            (
                {
                    "title": "",
                    "category_id": str(uuid.uuid4()),
                    "tag_ids": [str(uuid.uuid4())],
                    "end_at": "invalid-date",
                },
                {"title", "category_id", "tag_ids", "end_at"},
            ),
        ],
    )
    def test_create_with_validation_error(
        self,
        client: ninja_test.TestClient,
        mock_data: MockData,
        invalid_values: dict[str, t.Any],
        expected_error_fields: set[str],
    ) -> None:
        user, _, _, _ = mock_data

        base_data = {
            "title": "New Task",
        }
        invalid_data = base_data.copy() if invalid_values.keys() else {}
        invalid_data.update(dict(invalid_values.items()))

        response = client.post("", json=invalid_data, user=user)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_messages = response.data["detail"]
        for field in expected_error_fields:
            assert any(
                field in item.get("loc", []) for item in error_messages
            ), f"Field {field} not found in validation errors"
