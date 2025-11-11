from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from .serializers import get_from_serializer_data_or_instance


def validate_charfield_entry(value, allow_apostrophe=False):
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


def validate_phone_number(value):
    try:
        int(value.strip().lstrip("0+").replace("-", "").replace(" ", ""))
    except (ValueError, TypeError) as exc:
        raise ValidationError(_("Invalid mobile phonenumber.")) from exc

    return value


def validate_date(start_date: datetime | None, end_date: datetime | None) -> None:
    """
    Validates that the end date is greater than the start date.

    Raises:
        ValidationError: If `end_date` is not greater than `start_date`.
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
        except Exception:
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
    CustomRegexValidator because the validated value is append to the message.
    """

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not self.regex.search(force_str(value)):
            message = f"{self.message}: {force_str(value)}"
            raise ValidationError(message, code=self.code)


validate_postal_code = CustomRegexValidator(
    regex="^[1-9][0-9]{3} ?[a-zA-Z]{2}$", message=_("Invalid postal code.")
)
