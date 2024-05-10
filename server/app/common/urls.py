from django.urls import path

from server.app.common import views

app_name = "common"
urlpatterns = [
    path("health", views.health, name="health"),
    path("version", views.version, name="version"),
]
