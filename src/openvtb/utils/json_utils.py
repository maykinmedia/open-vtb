from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import structlog
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for

from .typing import JSONObject

logger = structlog.stdlib.get_logger(__name__)


def get_json_schema(key: str, schema_mapping: dict[str, JSONObject]) -> JSONObject:
    """
    Retrieve a JSON schema from SCHEMA_MAPPING by key.

    Args:
        key (str): The key identifying the schema.
        schema_mapping (dict[str, JSONObject]): Schema_mapping
    Raises:
        ValidationError: If no schema is found for the given key.

    Returns:
        JSONObject: The JSON schema associated with the key.
    """
    schema = schema_mapping.get(key)
    if not schema:
        raise ValidationError(
            _("Onbekend '{key}': geen schema beschikbaar.".format(key=key)),
            code="unknown_choice",
        )
    return schema


def check_json_schema(json_schema: JSONObject) -> None:
    """
    Check if a JSON schema is valid.

    Args:
        json_schema (JSONObject): The JSON schema to validate.

    Raises:
        ValidationError: If the schema is invalid.
    """
    schema_validator = validator_for(json_schema)
    try:
        schema_validator.check_schema(json_schema)
    except SchemaError as exc:
        raise ValidationError(str(exc))
