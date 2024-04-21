from django.shortcuts import render
from drfpasswordless.serializers import MobileAuthSerializer
from drfpasswordless.settings import api_settings
from drfpasswordless.views import AbstractBaseObtainAuthToken
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import CallbackToken, User
from user.serializers import CallbackTokenAuthSerializer, UserRetrieveSerializer
from user.services import TokenService


class AbstractBaseObtainCallbackToken(APIView):
    """
    This returns a 6-digit callback token we can trade for a user's Auth Token.
    """

    success_response = "A login token has been sent to you."
    failure_response = "Unable to send you a login code. Try again later."

    message_payload = {}

    @property
    def serializer_class(self):
        # Our serializer depending on type
        raise NotImplementedError

    @property
    def alias_type(self):
        # Alias Type
        raise NotImplementedError

    @property
    def token_type(self):
        # Token Type
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        if self.alias_type.upper() not in api_settings.PASSWORDLESS_AUTH_TYPES:
            # Only allow auth types allowed in settings.
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            # Validate -
            user = serializer.validated_data["user"]
            # Create and send callback token
            # use overridden 'TokenService' class
            success = TokenService.send_token(
                user, self.alias_type, self.token_type, **self.message_payload
            )
            # Respond With Success Or Failure of Sent
            if success:
                status_code = status.HTTP_200_OK
                response_detail = self.success_response
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                response_detail = self.failure_response
            return Response({"detail": response_detail}, status=status_code)
        else:
            return Response(
                serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
            )


class ObtainMobileCallbackToken(AbstractBaseObtainCallbackToken):
    permission_classes = (AllowAny,)
    serializer_class = MobileAuthSerializer
    success_response = "We texted you a login code."
    failure_response = "Unable to send you a login code. Try again later."

    alias_type = "mobile"
    token_type = CallbackToken.TOKEN_TYPE_AUTH

    mobile_message = api_settings.PASSWORDLESS_MOBILE_MESSAGE
    message_payload = {"mobile_message": mobile_message}


class ObtainAuthTokenFromCallbackToken(AbstractBaseObtainAuthToken):
    """
    This is a duplicate of rest_framework's own ObtainAuthToken method.
    Instead, this returns an Auth Token based on our callback token and source.
    """

    permission_classes = (AllowAny,)
    serializer_class = CallbackTokenAuthSerializer


class UserRetrieveAPIView(generics.RetrieveAPIView):
    lookup_field = "id"
    lookup_url_kwarg = "id"
    permission_classes = (IsAuthenticated,)
    serializer_class = UserRetrieveSerializer
    queryset = User.objects
