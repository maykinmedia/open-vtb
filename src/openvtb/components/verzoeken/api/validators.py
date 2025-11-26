from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import get_attribute

from ..constants import VerzoekTypeVersionStatus
from ..utils import check_json_schema


class VersionStatusValidator:
    """
    Ensures that only versions with status `draft` can be updated.

    If the serializer is updating an existing instance and its status is not
    `draft`, a ValidationError is raised. On create, nothing happens.
    """

    message = _("Alleen `draft` kunnen worden gewijzigd.")
    code = "non-draft-version-update"
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = getattr(serializer, "instance", None)
        if not instance:
            return

        if instance.status != VerzoekTypeVersionStatus.DRAFT:
            raise serializers.ValidationError(
                {"status": self.message},
                code=self.code,
            )


class JsonSchemaValidator:
    """
    Validates that the given value is a valid JSON Schema.

    Calls `check_json_schema` and raises a `ValidationError` if the schema
    is invalid.
    """

    code = "invalid-json-schema"

    def __call__(self, value):
        try:
            check_json_schema(value)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc


class CheckVerzoekTypeVersion:
    """
    Ensures that the given instance has a last version available.

    Raises a ValidationError if `instance.last_version` is None.
    """

    message = _("Onbekend VerzoekenType schema: geen schema beschikbaar.")
    code = "unknown-schema"

    def __call__(self, instance):
        if not instance.last_version:
            raise serializers.ValidationError(self.message, code=self.code)


class IsImmutableValidator:
    """
    Validator to ensure that a field cannot be changed on update.

    If the serializer is updating an existing instance and the field value
    differs from the current value, a ValidationError is raised.
    """

    message = _("Dit veld kan niet worden gewijzigd.")
    code = "immutable-field"
    requires_context = True

    def __call__(self, new_value, serializer_field):
        instance = getattr(serializer_field.parent, "instance", None)
        if not instance:
            return

        current_value = get_attribute(instance, serializer_field.source_attrs)

        if new_value != current_value:
            raise serializers.ValidationError(self.message, code=self.code)
