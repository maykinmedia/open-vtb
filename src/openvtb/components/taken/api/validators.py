from django.core.exceptions import ValidationError

from rest_framework import serializers

from openvtb.utils.api_utils import get_from_serializer_data_or_instance
from openvtb.utils.validators import validate_jsonschema

from ..schemas import FORMULIER_DEFINITIE_SCHEMA


class FormulierDefinitieValidator:
    """
    Validates the ``formulier_definitie`` field against ``FORMULIER_DEFINITIE_SCHEMA``.
    Raises a DRF ``ValidationError`` if the JSON Schema validation fails.
    """

    code = "invalid-json-schema"
    label = "formulierDefinitie"
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = get_from_serializer_data_or_instance(
            "formulier_definitie", attrs, serializer
        )
        if not instance:
            return

        try:
            validate_jsonschema(
                instance=instance,
                label=self.label,
                schema=FORMULIER_DEFINITIE_SCHEMA,
            )
        except ValidationError as error:
            raise serializers.ValidationError(error.message_dict, code=self.code)
        return attrs
