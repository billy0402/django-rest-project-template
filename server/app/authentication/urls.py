from django.urls import path
from rest_framework_simplejwt import views as jwt_views

app_name = "authentication"

urlpatterns = [
    path("obtain", jwt_views.TokenObtainPairView.as_view(), name="obtain"),
    path("refresh", jwt_views.TokenRefreshView.as_view(), name="refresh"),
    path("verify", jwt_views.TokenVerifyView.as_view(), name="verify"),
]
