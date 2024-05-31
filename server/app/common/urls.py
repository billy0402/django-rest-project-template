from django.urls import path

from server.app.common import views as common_views

app_name = "common"

urlpatterns = [
    path("health", common_views.health, name="health"),
    path("version", common_views.version, name="version"),
]
