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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular import views as docs_views
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

api_urlpatterns = [
    path("", include(router.urls)),
    path("_/", include("server.app.common.urls")),
    path("auth/", include("server.app.authentication.urls")),
]

urlpatterns = [
    # API
    path("api/v1/", include((api_urlpatterns, "v1"))),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # API Docs
    path("api/schema.json", docs_views.SpectacularAPIView.as_view(), name="schema"),
    path("api/swagger", docs_views.SpectacularSwaggerView.as_view(), name="swagger"),
    path("api/redoc", docs_views.SpectacularRedocView.as_view(), name="redoc"),
    # Admin
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if url_prefix := getattr(settings, "URL_PREFIX", None):
    urlpatterns = [path(url_prefix, include(urlpatterns))]
