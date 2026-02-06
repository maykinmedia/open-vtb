from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openvtb.utils.validators import validate_jsonschema

from .schemas import IS_INGEDIEND_DOOR_SCHEMA


class IsIngediendDoorValidator:
    """
    Validates `is_ingediend_door` against the IS_INGEDIEND_DOOR_SCHEMA
    """

    code = "invalid-json-schema"

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __call__(self, attrs):
        data = attrs.get(self.field_name, {})

        if not data:
            return attrs

        if len(data.keys()) > 1:
            raise serializers.ValidationError(
                {
                    self.field_name: _(
                        "It must have only one of the three permitted keys: "
                        "one of `authentiekeVerwijzing`, `nietAuthentiekePersoonsgegevens` or `nietAuthentiekeOrganisatiegegevens`."
                    ),
                }
            )
        try:
            validate_jsonschema(
                instance=data,
                schema=IS_INGEDIEND_DOOR_SCHEMA,
                label=self.field_name,
            )
        except ValidationError as error:
            raise serializers.ValidationError(error.message_dict, code=self.code)
        return attrs
