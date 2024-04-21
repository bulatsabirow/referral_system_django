import string
from dataclasses import dataclass, field

from django.utils.crypto import get_random_string


@dataclass
class InviteCode:
    code: str = field(init=False)
    length: int = 6

    def __post_init__(self):
        self.code = self.generate_invite_code()

    def generate_invite_code(self):
        return get_random_string(
            length=self.length, allowed_chars=string.ascii_uppercase + string.digits
        )
