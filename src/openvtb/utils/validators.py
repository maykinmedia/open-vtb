from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from .serializers import get_from_serializer_data_or_instance


def validate_charfield_entry(value: str, allow_apostrophe: bool = False) -> str:
    """
    Validates a charfield entry according with Belastingdienst requirements.

    :param value: The input value string to be validated.
    :param allow_apostrophe: Boolean to add the apostrophe character to the
    validation. Apostrophes are allowed in input with ``True`` value. Defaults
    to ``False``.
    :return: The input value if validation passed. Otherwise, raises a
    ``ValidationError`` exception.
    """
    invalid_chars = '/"\\,;' if allow_apostrophe else "/\"\\,;'"

    for char in invalid_chars:
        if char in value:
            raise ValidationError(
                _("The provided value contains an invalid character: %s") % char
            )
    return value


def validate_phone_number(value: str) -> str:
    """
    Validate a mobile phone number.

    Strips spaces, hyphens, and leading zeros or plus signs, then checks if
    the remaining value is numeric.

    Args:
        value (str): The phone number to validate.

    Returns:
        str: The original phone number if valid.

    Raises:
        ValidationError: If the value is not a valid numeric phone number.
    """
    try:
        int(value.strip().lstrip("0+").replace("-", "").replace(" ", ""))
    except (ValueError, TypeError) as exc:
        raise ValidationError(_("Invalid mobile phonenumber.")) from exc

    return value


def validate_date(start_date: datetime | None, end_date: datetime | None) -> None:
    """
    Validate that `end_date` is after `start_date`.

    Args:
        start_date (datetime | None): The starting date.
        end_date (datetime | None): The ending date.

    Returns:
        None

    Raises:
        ValidationError: If both dates are provided and `end_date` < `start_date`.

    """

    if start_date and end_date and end_date < start_date:
        raise ValidationError(
            _(
                "{end_date} date must be greater than {start_date}.".format(
                    end_date=str(end_date), start_date=str(start_date)
                )
            )
        )


class StartBeforeEndValidator:
    """
    Validate that start date is before the end date
    """

    code = "date-mismatch"
    message = _("{} should be before {}.")
    requires_context = True

    def __init__(self, start_date_field, end_date_field):
        self.start_date_field = start_date_field
        self.end_date_field = end_date_field

    def __call__(self, attrs, serializer):
        start_date = get_from_serializer_data_or_instance(
            self.start_date_field, attrs, serializer
        )
        end_date = get_from_serializer_data_or_instance(
            self.end_date_field, attrs, serializer
        )
        try:
            validate_date(start_date, end_date)
        except ValidationError:
            raise serializers.ValidationError(
                {
                    self.end_date_field: self.message.format(
                        self.start_date_field, self.end_date_field
                    ),
                },
                code=self.code,
            )


class CustomRegexValidator(RegexValidator):
    """
    Regex validator that appends the invalid value to the error message.
    """

    def __call__(self, value: Any) -> None:
        """
        Validate that the input matches the regular expression.

        Args:
            value (Any): The value to validate.

        Raises:
            ValidationError: If the value does not match the regex.
        """
        if not self.regex.search(force_str(value)):
            message = f"{self.message}: {force_str(value)}"
            raise ValidationError(message, code=self.code)
