from drf_spectacular import utils as docs_utils
from rest_framework import decorators, request, response

from server.app.common import serializers as common_serializers


@docs_utils.extend_schema(responses=common_serializers.HealthSerializer)
@decorators.api_view(["GET"])
def health(request: request.Request) -> response.Response:
    """Get API health status."""
    return response.Response({"status": True})


@docs_utils.extend_schema(responses=common_serializers.VersionSerializer)
@decorators.api_view(["GET"])
def version(request: request.Request) -> response.Response:
    """Get API version."""
    return response.Response({"version": 1})
