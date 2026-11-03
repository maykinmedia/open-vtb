from django.apps import AppConfig

from rest_framework.serializers import ModelSerializer
from vng_api_common.fields import URNField
from vng_api_common.serializers import URNField as URNSerializerField


class UtilsConfig(AppConfig):
    name = "openvtb.utils"

    def ready(self):
        from .oidc_auth import plugins  # noqa

        field_mapping = ModelSerializer.serializer_field_mapping
        field_mapping[URNField] = URNSerializerField
