import string

from django.conf import settings
from django.utils.crypto import get_random_string


def generate_numeric_token():
    """
    Generate a random 6 digit string of numbers.
    We use this formatting to allow leading 0s.
    """
    return get_random_string(
        length=settings.CALLBACK_TOKEN_LENGTH, allowed_chars=string.digits
    )
