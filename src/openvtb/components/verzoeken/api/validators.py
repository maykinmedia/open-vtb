from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..constants import VerzoekTypeVersionStatus
from ..utils import check_json_schema


class VersionUpdateValidator:
    message = _("Only draft versions can be changed")
    code = "non-draft-version-update"
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = getattr(serializer, "instance", None)
        if not instance:
            return

        if instance.status != VerzoekTypeVersionStatus.DRAFT:
            raise serializers.ValidationError(self.message, code=self.code)


class JsonSchemaValidator:
    code = "invalid-json-schema"

    def __call__(self, value):
        try:
            check_json_schema(value)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc
