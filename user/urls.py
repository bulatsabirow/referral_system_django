from django.urls import path

from user.views import (
    ObtainMobileCallbackToken,
    ObtainAuthTokenFromCallbackToken,
    UserRetrieveAPIView,
)

urlpatterns = [
    path("auth/mobile/", ObtainMobileCallbackToken.as_view(), name="auth-mobile"),
    path("auth/token/", ObtainAuthTokenFromCallbackToken.as_view(), name="auth-token"),
    path("user/<int:id>", UserRetrieveAPIView.as_view(), name="user"),
]
