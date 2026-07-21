import re

from django.core.exceptions import ValidationError


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cnpj(value: str) -> bool:
    digits = digits_only(value)
    if len(digits) != 14 or digits == digits[0] * 14:
        return False
    numbers = [int(char) for char in digits]
    for size, weights in (
        (12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]),
        (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]),
    ):
        total = sum(number * weight for number, weight in zip(numbers[:size], weights, strict=True))
        remainder = total % 11
        expected = 0 if remainder < 2 else 11 - remainder
        if numbers[size] != expected:
            return False
    return True


def validate_cnpj(value: str) -> None:
    if value and not is_valid_cnpj(value):
        raise ValidationError("Informe um CNPJ válido.")
