import re
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

import structlog
from jsonschema import (
    FormatChecker,
    FormatError,
    ValidationError as JSONValidationError,
    validate,
)

from .schemas import SCHEMA_MAPPING

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


def validate_jsonschema(data: Any, key: str) -> None:
    """
    Validator for JSONField with appropriate JSON schema.

    Args:
        data: The JSON data to validate.
        key: The key to lookup the schema in SCHEMA_MAPPING.

    Raises:
        ValidationError: If the data does not conform to the schema.
    """

    schema = SCHEMA_MAPPING.get(key, None)
    if not schema:
        logger.exception("validate_jsonschema failed: schema not found", schema_key=key)
        raise ValidationError(
            _("Onbekend '{key}': geen schema beschikbaar.".format(key=key)),
            code="unknown_choice",
        )

    try:
        validate(instance=data, schema=schema, format_checker=format_checker)
    except JSONValidationError as json_error:
        logger.exception(
            "validate_jsonschema failed: JSON not valid",
            schema_key=key,
            error=str(json_error),
        )
        path = ".".join(getattr(json_error, "absolute_path", [])) or "data"
        raise ValidationError({path: json_error.message})
