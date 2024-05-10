"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.trailing_slash = ""

api_urlpatterns = [
    path("", include(router.urls)),
    path("_/", include("server.app.common.urls")),
]

urlpatterns = [
    # API
    path("api/v1/", include((api_urlpatterns, "v1"))),
    # API Docs
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/swagger", SpectacularSwaggerView.as_view(), name="swagger"),
    path("api/redoc", SpectacularRedocView.as_view(), name="redoc"),
    # Admin
    path("admin/", admin.site.urls),
]

if url_prefix := getattr(settings, "URL_PREFIX", None):
    urlpatterns = [path(url_prefix, include(urlpatterns))]
