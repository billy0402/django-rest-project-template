from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from server.app.common.serializers import HealthSerializer, VersionSerializer


@extend_schema(responses=HealthSerializer)
@api_view(["GET"])
def health(request: Request) -> Response:
    """Get API health status."""
    return Response({"status": True})


@extend_schema(responses=VersionSerializer)
@api_view(["GET"])
def version(request: Request) -> Response:
    """Get API version."""
    return Response({"version": 1})
