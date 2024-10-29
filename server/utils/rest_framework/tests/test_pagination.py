import typing as t

import pytest
from django.core import paginator as django_paginator
from rest_framework import request as drf_request
from rest_framework import test

from server.utils.rest_framework import pagination as util_pagination


@pytest.fixture
def factory() -> test.APIRequestFactory:
    return test.APIRequestFactory()


@pytest.fixture
def pagination() -> util_pagination.PageNumberPagination:
    return util_pagination.PageNumberPagination()


@pytest.fixture
def mock_pages() -> list[int]:
    return list(range(1, 101))


@pytest.fixture
def paginated_request(
    factory: test.APIRequestFactory,
    pagination: util_pagination.PageNumberPagination,
    mock_pages: list[int],
) -> util_pagination.PageNumberPagination:
    request = factory.get("/api/items")
    paginator = django_paginator.Paginator(mock_pages, per_page=10)
    page = paginator.page(1)

    pagination.page = page
    pagination.request = drf_request.Request(request)
    return pagination


class TestPageNumberPagination:
    def test_page_size_query_param(self) -> None:
        pagination = util_pagination.PageNumberPagination()
        assert pagination.page_size_query_param == "limit"

    def test_max_page_size(self) -> None:
        pagination = util_pagination.PageNumberPagination()
        assert pagination.max_page_size == 1000  # noqa: PLR2004

    def test_get_first_link(
        self,
        paginated_request: util_pagination.PageNumberPagination,
    ) -> None:
        first_link = paginated_request.get_first_link()
        assert "page=1" in first_link
        assert first_link.startswith("http://testserver/api/items")

    def test_get_last_link(
        self,
        paginated_request: util_pagination.PageNumberPagination,
    ) -> None:
        last_link = paginated_request.get_last_link()
        assert "page=10" in last_link  # 100 items / 10 per page = 10 pages
        assert last_link.startswith("http://testserver/api/items")

    def test_paginated_response_structure(
        self,
        paginated_request: util_pagination.PageNumberPagination,
    ) -> None:
        response = paginated_request.get_paginated_response(data=[1, 2, 3])
        response_data = t.cast(dict[str, t.Any], response.data)

        assert "count" in response_data
        assert "page" in response_data
        assert "limit" in response_data
        assert "last" in response_data
        assert "results" in response_data
        assert "links" in response_data

        links = response_data["links"]
        assert "first" in links
        assert "previous" in links
        assert "current" in links
        assert "next" in links
        assert "last" in links

    def test_paginated_response_values(
        self,
        paginated_request: util_pagination.PageNumberPagination,
    ) -> None:
        response = paginated_request.get_paginated_response(data=[1, 2, 3])
        response_data = t.cast(dict[str, t.Any], response.data)

        assert response_data["count"] == 100  # noqa: PLR2004
        assert response_data["page"] == 1
        assert response_data["limit"] == 10  # noqa: PLR2004
        assert response_data["last"] == 10  # noqa: PLR2004
        assert response_data["results"] == [1, 2, 3]

    def test_paginated_response_links(
        self,
        paginated_request: util_pagination.PageNumberPagination,
    ) -> None:
        response = paginated_request.get_paginated_response(data=[1, 2, 3])
        response_data = t.cast(dict[str, t.Any], response.data)
        links = response_data["links"]

        assert "page=1" in links["first"]
        assert links["previous"] is None  # No previous page when on first page
        assert "/api/items" in links["current"]
        assert "page=2" in links["next"]
        assert "page=10" in links["last"]

    def test_schema_generation(
        self,
        pagination: util_pagination.PageNumberPagination,
    ) -> None:
        test_schema = {"type": "array", "items": {"type": "integer"}}
        schema = pagination.get_paginated_response_schema(test_schema)

        assert schema["type"] == "object"
        assert "count" in schema["properties"]
        assert "page" in schema["properties"]
        assert "limit" in schema["properties"]
        assert "last" in schema["properties"]
        assert "results" in schema["properties"]
        assert "links" in schema["properties"]

        links = schema["properties"]["links"]["properties"]
        assert "page=1" in links["first"]["example"]
        assert "page=2" in links["previous"]["example"]
        assert "page=3" in links["current"]["example"]
        assert "page=4" in links["next"]["example"]
        assert "page=13" in links["last"]["example"]

    @pytest.mark.parametrize(
        ("page_number", "expected_previous", "expected_next"),
        [
            (1, None, 2),  # First page
            (5, 4, 6),  # Middle page
            (10, 9, None),  # Last page
        ],
    )
    def test_pagination_navigation_links(  # noqa: PLR0913
        self,
        factory: test.APIRequestFactory,
        pagination: util_pagination.PageNumberPagination,
        mock_pages: list[int],
        page_number: int,
        expected_next: int | None,
        expected_previous: int | None,
    ) -> None:
        request = factory.get(f"/api/items?page={page_number}")
        paginator = django_paginator.Paginator(mock_pages, per_page=10)
        page = paginator.page(page_number)

        pagination.page = page
        pagination.request = drf_request.Request(request)

        response = pagination.get_paginated_response(data=list(page))
        response_data = t.cast(dict[str, t.Any], response.data)
        links = response_data["links"]

        if expected_next:
            assert f"page={expected_next}" in links["next"]
        else:
            assert links["next"] is None

        if expected_previous:
            assert f"page={expected_previous}" in links["previous"]
        else:
            assert links["previous"] is None
