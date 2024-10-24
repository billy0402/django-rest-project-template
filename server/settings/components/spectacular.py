SPECTACULAR_SETTINGS = {
    "TITLE": "Django REST project API",
    "DESCRIPTION": "A RESTful API",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_PERMISSIONS": [
        "rest_framework.permissions.IsAdminUser",
    ],
}
