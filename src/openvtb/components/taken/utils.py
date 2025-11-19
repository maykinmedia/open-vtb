from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import structlog

from .schemas import SCHEMA_MAPPING

logger = structlog.stdlib.get_logger(__name__)


def get_json_schema(key: str) -> Any:
    """
    Retrieve a JSON schema from SCHEMA_MAPPING by key.

    Args:
        key (str): The key identifying the schema.

    Raises:
        ValidationError: If no schema is found for the given key.

    Returns:
        Any: The JSON schema associated with the key.
    """
    schema = SCHEMA_MAPPING.get(key)
    if not schema:
        logger.exception(
            "validate_jsonschema failed: schema not found", extra={"schema_key": key}
        )
        raise ValidationError(
            _("Onbekend '{key}': geen schema beschikbaar.".format(key=key)),
            code="unknown_choice",
        )
    return schema
