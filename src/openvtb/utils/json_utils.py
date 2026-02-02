from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import structlog

from .typing import JSONObject

logger = structlog.stdlib.get_logger(__name__)


def get_json_schema(key: str, schema_mapping: dict[str, JSONObject]) -> JSONObject:
    """
    Retrieve a JSON schema from SCHEMA_MAPPING by key.

    Args:
        key (str): The key identifying the schema.
        schema_mapping (Any): schema_mapping
    Raises:
        ValidationError: If no schema is found for the given key.

    Returns:
        Any: The JSON schema associated with the key.
    """
    schema = schema_mapping.get(key)
    if not schema:
        raise ValidationError(
            _("Onbekend '{key}': geen schema beschikbaar.".format(key=key)),
            code="unknown_choice",
        )
    return schema
