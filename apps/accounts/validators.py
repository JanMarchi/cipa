from django.contrib.auth.password_validation import (
    MinimumLengthValidator as DjangoMinimumLengthValidator,
)
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext


class MinimumLengthValidator(DjangoMinimumLengthValidator):
    def validate(self, password: str, user: object | None = None) -> None:
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "A senha deve conter pelo menos %(min_length)d caractere.",
                    "A senha deve conter pelo menos %(min_length)d caracteres.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )
