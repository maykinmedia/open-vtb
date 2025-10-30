from django.core.exceptions import ValidationError

import jsonschema

from .schemas import SCHEMA_MAPPING


def validate_jsonschema(data, instance=None):
    """
    Validator for JSONField with appropriate JSON schema
    """

    taak_soort = getattr(instance, "taak_soort", None)
    if not taak_soort:
        return

    schema = SCHEMA_MAPPING.get(taak_soort, None)
    if not schema:
        return

    data_to_validate = data or {}
    try:
        jsonschema.validate(instance=data_to_validate, schema=schema)
    except jsonschema.ValidationError as json_error:
        raise ValidationError({"data": json_error.message})
