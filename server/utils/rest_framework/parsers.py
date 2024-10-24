import io
import json
import typing as t

from django import http
from rest_framework import parsers, request


class MultipartJsonParser(parsers.MultiPartParser):
    def parse(
        self,
        stream: io.BytesIO | request.Request | http.HttpRequest,
        media_type: str | None = None,
        parser_context: dict[str, t.Any] | None = None,
    ) -> parsers.DataAndFiles:
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context,
        )
        data: dict[str, t.Any] = {}

        for key, value in result.data.items():
            if "{" in value or "[" in value:
                try:
                    data[key] = json.loads(value)
                except ValueError:
                    data[key] = value

            else:
                data[key] = value

        return parsers.DataAndFiles(data, result.files)
