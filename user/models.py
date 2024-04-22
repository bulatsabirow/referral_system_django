from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from drfpasswordless.models import AbstractBaseCallbackToken
from phonenumber_field.modelfields import PhoneNumberField

from user.schema import InviteCode
from user.services import generate_numeric_token


def get_invite_code():
    return InviteCode().code


class User(AbstractBaseUser):
    mobile = PhoneNumberField(
        max_length=12, unique=True, validators=[MinLengthValidator(12)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(
        max_length=InviteCode.length, default=get_invite_code, unique=True
    )
    referrer = models.ForeignKey(
        "self",
        related_name="referee_set",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []

    def __str__(self):
        return "%s(mobile=%s)" % (self.__class__.__name__, self.mobile)


class CallbackToken(AbstractBaseCallbackToken):
    """
    Generates a random digit number having certain length to be returned.
    """

    TOKEN_TYPE_AUTH = "AUTH"
    TOKEN_TYPE_VERIFY = "VERIFY"
    TOKEN_TYPES = ((TOKEN_TYPE_AUTH, "Auth"), (TOKEN_TYPE_VERIFY, "Verify"))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="callback_tokens",
        on_delete=models.CASCADE,
    )
    key = models.CharField(
        default=generate_numeric_token, max_length=settings.CALLBACK_TOKEN_LENGTH
    )
    type = models.CharField(max_length=20, choices=TOKEN_TYPES)

    class Meta(AbstractBaseCallbackToken.Meta):
        verbose_name = "Callback Token"
