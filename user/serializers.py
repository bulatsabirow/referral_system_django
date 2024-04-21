from django.conf import settings
from django.contrib.auth import get_user_model
from drfpasswordless.serializers import (
    AbstractBaseCallbackTokenSerializer as DjangoAbstractBaseCallbackTokenSerializer,
    TokenField,
)
from drfpasswordless.settings import api_settings
from drfpasswordless.utils import verify_user_alias
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.models import CallbackToken
from django.utils.translation import gettext_lazy as _

from user.services import validate_token_age

User = get_user_model()


def token_age_validator(value):
    """
    Check token age
    Makes sure a token is within the proper expiration datetime window.
    """
    valid_token = validate_token_age(value)
    if not valid_token:
        raise serializers.ValidationError("The token you entered isn't valid.")
    return value


class AbstractBaseCallbackTokenSerializer(DjangoAbstractBaseCallbackTokenSerializer):
    token = TokenField(
        min_length=settings.CALLBACK_TOKEN_LENGTH,
        max_length=settings.CALLBACK_TOKEN_LENGTH,
        validators=[token_age_validator],
    )


class CallbackTokenAuthSerializer(AbstractBaseCallbackTokenSerializer):
    def validate(self, attrs):
        # Check Aliases
        try:
            alias_type, alias = self.validate_alias(attrs)
            callback_token = attrs.get("token", None)
            user = User.objects.get(**{alias_type + "__iexact": alias})
            token = CallbackToken.objects.get(
                **{
                    "user": user,
                    "key": callback_token,
                    "type": CallbackToken.TOKEN_TYPE_AUTH,
                    "is_active": True,
                }
            )

            if token.user == user:
                # Check the token type for our uni-auth method.
                # authenticates and checks the expiry of the callback token.
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg)

                if (
                    api_settings.PASSWORDLESS_USER_MARK_EMAIL_VERIFIED
                    or api_settings.PASSWORDLESS_USER_MARK_MOBILE_VERIFIED
                ):
                    # Mark this alias as verified
                    user = User.objects.get(pk=token.user.pk)
                    success = verify_user_alias(user, token)

                    if success is False:
                        msg = _("Error validating user alias.")
                        raise serializers.ValidationError(msg)

                attrs["user"] = user
                return attrs

            else:
                msg = _("Invalid Token")
                raise serializers.ValidationError(msg)
        except CallbackToken.DoesNotExist:
            msg = _("Invalid alias parameters provided.")
            raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            msg = _("Invalid user alias parameters provided.")
            raise serializers.ValidationError(msg)
        except ValidationError:
            msg = _("Invalid alias parameters provided.")
            raise serializers.ValidationError(msg)
