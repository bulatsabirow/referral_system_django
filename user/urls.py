from django.urls import path

from user.views import (
    ObtainMobileCallbackToken,
    ObtainAuthTokenFromCallbackToken,
    UserRetrieveUpdateAPIView,
)

urlpatterns = [
    path("auth/mobile/", ObtainMobileCallbackToken.as_view(), name="auth-mobile"),
    path("auth/token/", ObtainAuthTokenFromCallbackToken.as_view(), name="auth-token"),
    path("user", UserRetrieveUpdateAPIView.as_view(), name="user"),
]
