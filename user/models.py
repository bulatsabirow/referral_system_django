from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.db import models
from drfpasswordless.models import AbstractBaseCallbackToken
from phonenumber_field.modelfields import PhoneNumberField


from user.services import generate_numeric_token


class User(AbstractBaseUser):
    mobile = PhoneNumberField(max_length=12, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []


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
