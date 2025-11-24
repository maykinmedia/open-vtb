from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from vng_api_common.serializers import CachedHyperlinkedRelatedField
from vng_api_common.utils import get_help_text

from ..models import (
    Verzoek,
    VerzoekBetaling,
    VerzoekBron,
    VerzoekType,
    VerzoekTypeVersion,
)
from .validators import JsonSchemaValidator, VersionUpdateValidator


class VerzoekTypeVersionSerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {"verzoektype_uuid": "verzoek_type__uuid"}

    class Meta:
        model = VerzoekTypeVersion
        fields = (
            "url",
            "version",
            "verzoek_type",
            "status",
            "aanvraag_gegevens_schema",
            "created_at",
            "modified_at",
            "published_at",
        )
        extra_kwargs = {
            "url": {
                "lookup_field": "version",
                "lookup_url_kwarg": "verzoektype_version",
                "view_name": "verzoeken:verzoektypeversion-detail",
                "help_text": _("De unieke URL van de verzoek deze API."),
            },
            "version": {"read_only": True},
            "verzoek_type": {
                "lookup_field": "uuid",
                "view_name": "verzoeken:verzoektype-detail",
                "read_only": True,
            },
            "aanvraag_gegevens_schema": {"validators": [JsonSchemaValidator()]},
            "created_at": {"read_only": True},
            "modified_at": {"read_only": True},
            "published_at": {"read_only": True},
        }
        validators = [VersionUpdateValidator()]


class VerzoekBronSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerzoekBron
        fields = ("naam", "kenmerk")


class VerzoekBetalingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerzoekBetaling
        fields = (
            "kenmerken",
            "bedrag",
            "voltooid",
            "transactie_datum",
            "transactie_referentie",
        )


class VerzoekTypeSerializer(serializers.ModelSerializer):
    version = NestedHyperlinkedRelatedField(
        read_only=True,
        source="last_version",
        lookup_field="version",
        lookup_url_kwarg="verzoektype_version",
        view_name="verzoeken:verzoektypeversion-detail",
        parent_lookup_kwargs={"verzoektype_uuid": "verzoek_type__uuid"},
        help_text=get_help_text("verzoeken.VerzoekTypeVersion", "version"),
    )

    aanvraag_gegevens_schema = serializers.JSONField(
        read_only=True,
        help_text=get_help_text(
            "verzoeken.VerzoekTypeVersion", "aanvraag_gegevens_schema"
        ),
    )

    class Meta:
        model = VerzoekType
        fields = (
            "url",
            "uuid",
            "version",
            "naam",
            "toelichting",
            "opvolging",
            "aanvraag_gegevens_schema",
        )

        extra_kwargs = {
            "uuid": {"read_only": True},
            "url": {
                "view_name": "verzoeken:verzoektype-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van de verzoek type deze API."),
            },
        }


class VerzoekSerializer(serializers.ModelSerializer):
    verzoek_type = CachedHyperlinkedRelatedField(
        view_name="verzoeken:verzoektype-detail",
        lookup_field="uuid",
        read_only=True,
        help_text=get_help_text("verzoeken.Verzoek", "verzoek_type"),
    )
    geometrie = GeometryField()
    verzoek_bron = VerzoekBronSerializer(source="bron")
    verzoek_betaling = VerzoekBetalingSerializer(source="betaling")

    class Meta:
        model = Verzoek
        fields = (
            "url",
            "uuid",
            "verzoek_type",
            "geometrie",
            "aanvraag_gegevens",
            "bijlagen",
            "verzoek_bron",
            "verzoek_betaling",
        )

        extra_kwargs = {
            "uuid": {"read_only": True},
            "url": {
                "view_name": "verzoeken:verzoek-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van de verzoek deze API."),
            },
        }
