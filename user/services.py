import string

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.module_loading import import_string
from drfpasswordless.settings import api_settings


def generate_numeric_token():
    """
    Generate a random 6 digit string of numbers.
    We use this formatting to allow leading 0s.
    """
    return get_random_string(
        length=settings.CALLBACK_TOKEN_LENGTH, allowed_chars=string.digits
    )


def create_callback_token_for_user(user, alias_type, token_type):
    from user.models import CallbackToken

    token = None
    alias_type_u = alias_type.upper()
    to_alias_field = getattr(
        api_settings, f"PASSWORDLESS_USER_{alias_type_u}_FIELD_NAME"
    )
    if user.pk in api_settings.PASSWORDLESS_DEMO_USERS.keys():
        token = CallbackToken.objects.filter(user=user).first()
        if token:
            return token
        else:
            return CallbackToken.objects.create(
                user=user,
                key=api_settings.PASSWORDLESS_DEMO_USERS[user.pk],
                to_alias_type=alias_type_u,
                to_alias=getattr(user, to_alias_field),
                type=token_type,
            )

    token = CallbackToken.objects.create(
        user=user,
        to_alias_type=alias_type_u,
        to_alias=getattr(user, to_alias_field),
        type=token_type,
    )

    if token is not None:
        return token

    return None


def validate_token_age(callback_token):
    """
    Returns True if a given token is within the age expiration limit.
    """
    from user.models import CallbackToken

    try:
        token = CallbackToken.objects.get(key=callback_token, is_active=True)
        seconds = (timezone.now() - token.created_at).total_seconds()
        token_expiry_time = api_settings.PASSWORDLESS_TOKEN_EXPIRE_TIME
        if token.user.pk in api_settings.PASSWORDLESS_DEMO_USERS.keys():
            return True
        if seconds <= token_expiry_time:
            return True
        else:
            # Invalidate our token.
            token.is_active = False
            token.save()
            return False

    except CallbackToken.DoesNotExist:
        # No valid token.
        return False


class TokenService(object):
    @staticmethod
    def create_token(user, alias_type, token_type):
        return create_callback_token_for_user(user, alias_type, token_type)

    @staticmethod
    def send_token(user, token, alias_type, **message_payload):
        send_action = None

        if user.pk in api_settings.PASSWORDLESS_DEMO_USERS.keys():
            return True
        if alias_type == "email":
            send_action = import_string(api_settings.PASSWORDLESS_EMAIL_CALLBACK)
        elif alias_type == "mobile":
            send_action = import_string(api_settings.PASSWORDLESS_SMS_CALLBACK)
        # Send to alias
        success = send_action(user, token, **message_payload)
        return success
