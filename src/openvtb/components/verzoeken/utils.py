from typing import Any, Mapping  # noqa

from django.core.exceptions import ValidationError

from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for

JsonSchemaType = Mapping[str, Any] | bool


def check_json_schema(json_schema: JsonSchemaType) -> None:
    """
    Check if a JSON schema is valid.

    Args:
        json_schema (dict): The JSON schema to validate.

    Raises:
        ValidationError: If the schema is invalid.
    """
    schema_validator = validator_for(json_schema)
    try:
        schema_validator.check_schema(json_schema)
    except SchemaError as exc:
        raise ValidationError(exc)
