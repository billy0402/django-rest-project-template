import typing as t
from collections import OrderedDict

from django.core.paginator import Page
from ninja import Schema
from ninja_extra import pagination

T = t.TypeVar("T")


class Links(Schema):
    first: str
    previous: str | None
    current: str
    next: str | None
    last: str


class CustomPagination(pagination.PageNumberPaginationExtra):
    page_size_query_param = "limit"
    max_page_size = 1000

    class Output(Schema, t.Generic[T]):  # type: ignore
        count: int
        limit: int
        page: int
        last: int
        results: list[T]
        links: Links

    def get_current_link(self, url: str, page: Page) -> str:
        return f"{url}&page={page.number}&{self.page_size_query_param}={page.paginator.per_page}"  # noqa: E501

    def get_first_link(self, url: str, page: Page) -> str:
        return f"{url}&page=1&{self.page_size_query_param}={page.paginator.per_page}"

    def get_last_link(self, url: str, page: Page) -> str:
        return f"{url}&page={page.paginator.num_pages}&{self.page_size_query_param}={page.paginator.per_page}"  # noqa: E501

    def get_paginated_response(
        self,
        *,
        base_url: str,
        page: Page,
    ) -> OrderedDict[str, t.Any]:
        links = OrderedDict(
            [
                ("first", self.get_first_link(base_url, page=page)),
                ("previous", self.get_previous_link(base_url, page=page)),
                ("current", self.get_current_link(base_url, page=page)),
                ("next", self.get_next_link(base_url, page=page)),
                ("last", self.get_last_link(base_url, page=page)),
            ],
        )
        response: OrderedDict[str, t.Any] = OrderedDict(
            [
                ("count", page.paginator.count),
                ("limit", page.paginator.per_page),
                ("page", page.number),
                ("last", page.paginator.num_pages),
                ("results", list(page)),
                ("links", links),
            ],
        )
        return response


PaginationOut = CustomPagination.Output
