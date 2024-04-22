from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from drfpasswordless.serializers import (
    AbstractBaseCallbackTokenSerializer as DjangoAbstractBaseCallbackTokenSerializer,
    TokenField,
    MobileAuthSerializer as DjangoMobileAuthSerializer,
)
from drfpasswordless.settings import api_settings
from drfpasswordless.utils import verify_user_alias
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.fields import PhoneNumberField
from user.models import CallbackToken
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


class MobileAuthSerializer(DjangoMobileAuthSerializer):
    phone_regex = RegexValidator(
        regex=rf"^\+[1-9]\d{settings.PHONENUMBER_LENGTH - 2}$",
        message="Mobile number must be entered in the format:" " '+11234567890'.",
    )
    mobile = serializers.CharField(
        validators=[phone_regex], max_length=settings.PHONENUMBER_LENGTH
    )


class AbstractBaseCallbackTokenSerializer(DjangoAbstractBaseCallbackTokenSerializer):
    phone_regex = RegexValidator(
        regex=rf"^\+[1-9]\d{settings.PHONENUMBER_LENGTH - 2}$",
        message="Mobile number must be entered in the format:" " '+11234567890'.",
    )
    mobile = serializers.CharField(
        validators=[phone_regex], max_length=settings.PHONENUMBER_LENGTH
    )
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


class UserRetrieveSerializer(serializers.ModelSerializer):
    activated_invite_code = serializers.CharField(allow_null=True)
    referee_set = serializers.ListSerializer(child=PhoneNumberField(), read_only=True)

    class Meta:
        model = User
        fields = ("id", "mobile", "invite_code", "activated_invite_code", "referee_set")


class InviteCodeActivateSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)

    def update(self, instance, validated_data):
        # check whether entered invite code exists or user try to activate its own invite code
        if (
            not User.objects.filter(invite_code=validated_data["invite_code"]).exists()
            or instance.invite_code == validated_data["invite_code"]
        ):
            raise serializers.ValidationError(detail=_("Invalid invite code."))

        referrer = User.objects.get(invite_code=validated_data["invite_code"])

        # check whether user have already activated any invite code
        if instance.referrer_id:
            raise serializers.ValidationError(
                detail=_("You already have activated invite code.")
            )

        instance.referrer_id = referrer.id
        instance.save()
        return instance
