from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from jsonschema import FormatChecker, ValidationError as JSONValidationError, validate

from .schemas import SCHEMA_MAPPING


def validate_jsonschema(data: Any, key: str) -> None:
    """
    Validator for JSONField with appropriate JSON schema.

    Args:
        data: The JSON data to validate.
        key: The key to lookup the schema in SCHEMA_MAPPING.

    Raises:
        ValidationError: If the data does not conform to the schema.
    """

    data = data or {}
    if data and not key:
        raise ValidationError(
            {
                "taak_soort": _(
                    "Dit veld is verplicht voordat u het veld 'data' kunt instellen"
                )
            }
        )

    schema = SCHEMA_MAPPING.get(key, None)
    if not schema:
        return
    try:
        validate(instance=data, schema=schema, format_checker=FormatChecker())
    except JSONValidationError as json_error:
        raise ValidationError({"data": json_error.message})
