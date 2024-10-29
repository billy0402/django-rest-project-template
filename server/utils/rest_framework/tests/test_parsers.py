import typing as t
from unittest import mock

import pytest
from django.http import HttpRequest
from rest_framework import parsers

from server.utils.rest_framework import parsers as util_parsers


@pytest.fixture
def parser() -> util_parsers.MultipartJsonParser:
    return util_parsers.MultipartJsonParser()


@pytest.fixture
def mock_parse() -> t.Generator[mock.MagicMock, None, None]:
    with mock.patch("rest_framework.parsers.MultiPartParser.parse") as mocker:
        yield mocker


class TestMultipartJsonParser:
    def test_parse_regular_form_data(
        self,
        parser: util_parsers.MultipartJsonParser,
        mock_parse: mock.MagicMock,
    ) -> None:
        mock_result = parsers.DataAndFiles(
            data={"name": "John", "age": "30"},
            files={"file": "dummy_file"},
        )
        mock_parse.return_value = mock_result

        result = parser.parse(mock.Mock())

        assert isinstance(result, parsers.DataAndFiles)
        assert result.data == {"name": "John", "age": "30"}
        assert result.files == {"file": "dummy_file"}

    def test_parse_json_in_form_data(
        self,
        parser: util_parsers.MultipartJsonParser,
        mock_parse: mock.MagicMock,
    ) -> None:
        mock_result = parsers.DataAndFiles(
            data={
                "user": '{"name": "John", "age": 30}',
                "preferences": '["reading", "gaming"]',
                "regular_field": "plain text",
            },
            files={},
        )
        mock_parse.return_value = mock_result

        result = parser.parse(mock.Mock())

        assert isinstance(result, parsers.DataAndFiles)
        assert result.data == {
            "user": {"name": "John", "age": 30},
            "preferences": ["reading", "gaming"],
            "regular_field": "plain text",
        }

    def test_parse_invalid_json_in_form_data(
        self,
        parser: util_parsers.MultipartJsonParser,
        mock_parse: mock.MagicMock,
    ) -> None:
        mock_result = parsers.DataAndFiles(
            data={
                "valid_json": '{"name": "John"}',
                "invalid_json": "{invalid_json}",
                "normal_field": "text with {brackets}",
            },
            files={},
        )
        mock_parse.return_value = mock_result

        result = parser.parse(mock.Mock())

        assert isinstance(result, parsers.DataAndFiles)
        assert result.data == {
            "valid_json": {"name": "John"},
            "invalid_json": "{invalid_json}",
            "normal_field": "text with {brackets}",
        }

    def test_parse_json_and_files(
        self,
        parser: util_parsers.MultipartJsonParser,
        mock_parse: mock.MagicMock,
    ) -> None:
        mock_file = mock.Mock()
        mock_result = parsers.DataAndFiles(
            data={
                "title": "Document",
                "metadata": '{"description": "test file", "tags": ["important"]}',
            },
            files={"document": mock_file},
        )
        mock_parse.return_value = mock_result

        result = parser.parse(mock.Mock())

        assert isinstance(result, parsers.DataAndFiles)
        assert result.data == {
            "title": "Document",
            "metadata": {"description": "test file", "tags": ["important"]},
        }
        assert result.files == {"document": mock_file}

    def test_parse_with_media_type_and_context(
        self,
        parser: util_parsers.MultipartJsonParser,
        mock_parse: mock.MagicMock,
    ) -> None:
        mock_stream = mock.Mock()
        media_type = "multipart/form-data"
        parser_context: dict[str, t.Any] = {"request": mock.Mock(spec=HttpRequest)}

        mock_result = parsers.DataAndFiles(data={"data": '{"key": "value"}'}, files={})
        mock_parse.return_value = mock_result

        result = parser.parse(
            mock_stream, media_type=media_type, parser_context=parser_context
        )

        mock_parse.assert_called_once_with(
            mock_stream, media_type=media_type, parser_context=parser_context
        )
        assert result.data == {"data": {"key": "value"}}
