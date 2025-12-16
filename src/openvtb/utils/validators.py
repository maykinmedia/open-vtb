import re
from datetime import datetime
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

import structlog
from jsonschema import (
    FormatChecker,
    FormatError,
    ValidationError as JSONValidationError,
    validate,
)
from rest_framework import serializers

from openvtb.utils.api_utils import get_from_serializer_data_or_instance

logger = structlog.stdlib.get_logger(__name__)
format_checker = FormatChecker()


@format_checker.checks("decimal")
def is_decimal(value: str) -> bool:
    """
    Checks that 'value' is a valid decimal with at most 2 decimal places.
    Raises ValidationError if invalid.
    """
    try:
        d = Decimal(value)
    except Exception:
        raise FormatError(
            _("'{value}' is not a valid decimal number".format(value=value))
        )
    if d.as_tuple().exponent < -2:
        raise FormatError(
            _("'{value}' has more than 2 decimal places".format(value=value))
        )
    return True


@format_checker.checks("iban")
def is_valid_iban(value: str) -> bool:
    """
    JSONSchema format checker for IBAN values.

    Raises:
        ValidationError: if the IBAN does not match the expected pattern.
    """
    iban_regex = r"^[A-Za-z]{2}[0-9]{2}[A-Za-z0-9]{1,30}$"
    if not re.compile(iban_regex).fullmatch(force_str(value)):
        raise FormatError(_("'{value}' is not a valid IBAN".format(value=value)))
    return True


def validate_jsonschema(instance: Any, schema: Any, label: str = "instance") -> None:
    """
    Validator for JSONField with appropriate JSON schema.

    Args:
        instance (Any): The JSON object to validate.
        label (str): A label representing the root key of the instance (used in error paths).
        schema (Any): The JSON Schema to validate against.

    Raises:
        ValueError: Raises a dictionary mapping the error path to the validation message.
    """
    try:
        validate(instance=instance, schema=schema, format_checker=format_checker)
    except JSONValidationError as json_error:
        logger.exception("validate_jsonschema failed: JSON not valid")

        path_list = [str(err) for err in getattr(json_error, "absolute_path", [])]
        if label not in path_list:
            path_list.insert(0, label)
        path = ".".join(path_list)

        raise ValidationError({path: json_error.message})


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


validate_postal_code = CustomRegexValidator(
    regex="^[1-9][0-9]{3} ?[a-zA-Z]{2}$", message=_("Invalid postal code.")
)


@deconstructible
class URNValidator(RegexValidator):
    """
    The basic syntax for a URN is defined using the
    Augmented Backus-Naur Form (ABNF) as specified in [RFC5234].

    URN Syntax:

        namestring    = assigned-name
                        [ rq-components ]
                        [ "#" f-component ]

        assigned-name = "urn" ":" NID ":" NSS

        NID           = (alphanum) 0*30(ldh) (alphanum)
        ldh           = alphanum / "-"
        NSS           = pchar *(pchar / "/")

        rq-components = [ "?+" r-component ]
                        [ "?=" q-component ]
        r-component   = pchar *( pchar / "/" / "?" )
        q-component   = pchar *( pchar / "/" / "?" )

        f-component   = fragment

        ; general URI syntax rules (RFC3986)
        fragment      = *( pchar / "/" / "?" )
        pchar         = unreserved / pct-encoded / sub-delims / ":" / "@"
        pct-encoded   = "%" HEXDIG HEXDIG
        unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
        sub-delims    = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="

        alphanum      = ALPHA / DIGIT  ; obsolete, usage is deprecated

    The question mark character "?" can be used without percent-encoding
    inside r-components, q-components, and f-components.  Other than
    inside those components, a "?" that is not immediately followed by
    "=" or "+" is not defined for URNs and SHOULD be treated as a syntax
    error by URN-specific parsers and other processors.

    https://datatracker.ietf.org/doc/html/rfc8141
    """

    HEXDIG = r"[0-9A-Fa-f]"
    ALPHANUM = r"[A-Za-z0-9]"
    pchar = rf"(?:{ALPHANUM}|[-._~]|%{HEXDIG}{HEXDIG}|[!$&'()*+,;=]|[:@])"

    # assigned-name
    NID = rf"{ALPHANUM}(?:{ALPHANUM}|-){{0,30}}{ALPHANUM}"
    NSS = rf"{pchar}(?:{pchar}|/)*"
    assigned_name = rf"urn:{NID}:{NSS}"

    # optional r/q components
    rq_components = (
        rf"(?:\?\+{pchar}(?:{pchar}|/|\?)*)?(?:\?={pchar}(?:{pchar}|/|\?)*)?"
    )

    # optional f-component
    f_component = rf"{pchar}(?:{pchar}|/|\?)*"

    # complete URN regex (RFC 8141)
    urn_pattern = rf"^{assigned_name}{rq_components}(?:#{f_component})?$"

    message = (
        "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' "
        "(e.g., urn:isbn:9780143127796)."
    )
    code = "invalid_urn"

    def __init__(self):
        super().__init__(
            regex=re.compile(self.urn_pattern),
            message=self.message,
            code=self.code,
        )
