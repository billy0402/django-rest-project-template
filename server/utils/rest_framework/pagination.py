import typing as t

from django.core import paginator
from rest_framework import pagination, request, response
from rest_framework.utils.urls import replace_query_param


class PageNumberPagination(pagination.PageNumberPagination):
    page: paginator.Page
    request: request.Request

    page_size_query_param = "limit"
    max_page_size = 1000

    def get_first_link(self) -> str:
        url = self.request.build_absolute_uri()
        page_number = 1
        return replace_query_param(url, self.page_query_param, page_number)

    def get_last_link(self) -> str:
        url = self.request.build_absolute_uri()
        page_number = self.page.paginator.num_pages
        return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data: t.Any) -> response.Response:
        return response.Response(
            {
                "count": self.page.paginator.count,
                "page": self.page.number,
                "limit": self.page.paginator.per_page,
                "last": self.page.paginator.num_pages,
                "results": data,
                "links": {
                    "first": self.get_first_link(),
                    "previous": self.get_previous_link(),
                    "current": self.request.build_absolute_uri(),
                    "next": self.get_next_link(),
                    "last": self.get_last_link(),
                },
            },
        )

    def get_paginated_response_schema(
        self,
        schema: dict[str, t.Any],
    ) -> dict[str, t.Any]:
        return {
            "type": "object",
            "required": ["count", "page", "limit", "last", "results"],
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "page": {
                    "type": "integer",
                    "example": 3,
                },
                "limit": {
                    "type": "integer",
                    "example": 10,
                },
                "last": {
                    "type": "integer",
                    "example": 13,
                },
                "results": schema,
                "links": {
                    "type": "object",
                    "required": ["first", "previous", "current", "next", "last"],
                    "properties": {
                        "first": {
                            "type": "string",
                            "format": "uri",
                            "example": f"http://api.example.org/accounts/?{self.page_query_param}=1",
                        },
                        "previous": {
                            "type": "string",
                            "nullable": True,
                            "format": "uri",
                            "example": f"http://api.example.org/accounts/?{self.page_query_param}=2",
                        },
                        "current": {
                            "type": "string",
                            "format": "uri",
                            "example": f"http://api.example.org/accounts/?{self.page_query_param}=3",
                        },
                        "next": {
                            "type": "string",
                            "nullable": True,
                            "format": "uri",
                            "example": f"http://api.example.org/accounts/?{self.page_query_param}=4",
                        },
                        "last": {
                            "type": "string",
                            "format": "uri",
                            "example": f"http://api.example.org/accounts/?{self.page_query_param}=13",
                        },
                    },
                },
            },
        }
