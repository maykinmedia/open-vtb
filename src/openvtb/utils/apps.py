from django.apps import AppConfig

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .fields import URNField


@extend_schema_field(
    {"type": "string", "example": "urn:namespace:component:resource:uuid"}
)
class URNSerializerField(serializers.CharField):
    """
    Mapping URNField to URNSerializerField
    """


class UtilsConfig(AppConfig):
    name = "openvtb.utils"

    def ready(self):
        field_mapping = ModelSerializer.serializer_field_mapping
        field_mapping[URNField] = URNSerializerField
