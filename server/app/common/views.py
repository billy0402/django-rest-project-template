from django import http
from ninja import Router

from server.app.common import schema as common_schema

router = Router()


@router.get("/health", response=common_schema.HealthOut)
def health(request: http.HttpRequest) -> dict:
    """Get API health status."""
    return {"status": True}


@router.get("/version", response=common_schema.VersionOut)
def version(request: http.HttpRequest) -> dict:
    """Get API version."""
    return {"version": 1}
