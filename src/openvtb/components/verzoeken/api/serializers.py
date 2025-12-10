from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from vng_api_common.serializers import CachedHyperlinkedRelatedField
from vng_api_common.utils import get_help_text

from openvtb.utils.api_utils import get_from_serializer_data_or_instance
from openvtb.utils.serializers import (
    URNModelSerializer,
    URNRelatedField,
)
from openvtb.utils.validators import validate_jsonschema

from ..models import (
    Verzoek,
    VerzoekBetaling,
    VerzoekBron,
    VerzoekType,
    VerzoekTypeVersion,
)
from .validators import (
    CheckVerzoekTypeVersion,
    IsImmutableValidator,
    JsonSchemaValidator,
    VersionStatusValidator,
)


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
                "help_text": _(
                    "De unieke URL van deze verzoektype versie binnen deze API."
                ),
            },
            "version": {"read_only": True},
            "verzoek_type": {
                "lookup_field": "uuid",
                "view_name": "verzoeken:verzoektype-detail",
                "read_only": True,
            },
            "aanvraag_gegevens_schema": {
                "validators": [JsonSchemaValidator()],
                "required": True,
            },
            "created_at": {"read_only": True},
            "modified_at": {"read_only": True},
            "published_at": {"read_only": True},
        }
        validators = [VersionStatusValidator()]

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        verzoektype_uuid = self.context["request"].resolver_match.kwargs.get(
            "verzoektype_uuid", ""
        )

        verzoek_type = VerzoekType.objects.filter(uuid=verzoektype_uuid).first()
        if not verzoek_type:
            raise serializers.ValidationError(
                _("VerzoekType with the specified UUID does not exist"),
                code="verzoektype-does-not-exist",
            )

        valid_attrs["verzoek_type"] = verzoek_type
        return valid_attrs


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


class VerzoekTypeSerializer(URNModelSerializer, serializers.ModelSerializer):
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
            "urn",
            "uuid",
            "version",
            "naam",
            "toelichting",
            "opvolging",
            "bijlage_typen",
            "aanvraag_gegevens_schema",
        )

        extra_kwargs = {
            "uuid": {"read_only": True},
            "url": {
                "view_name": "verzoeken:verzoektype-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van het verzoektype binnen deze API."),
            },
            "urn": {
                "lookup_field": "uuid",
                "help_text": _("De Uniform Resource Name van het verzoektype."),
            },
        }


class VerzoekSerializer(URNModelSerializer, serializers.ModelSerializer):
    verzoek_type = CachedHyperlinkedRelatedField(
        view_name="verzoeken:verzoektype-detail",
        lookup_field="uuid",
        required=True,
        queryset=VerzoekType.objects.all(),
        validators=[CheckVerzoekTypeVersion(), IsImmutableValidator()],
        help_text=get_help_text("verzoeken.Verzoek", "verzoek_type"),
    )
    verzoek_type_urn = URNRelatedField(
        lookup_field="uuid",
        source="verzoek_type",
        urn_resource="verzoektype",
        read_only=True,
        help_text=get_help_text("verzoeken.Verzoek", "verzoek_type") + _("URN field"),
    )
    geometrie = GeometryField(
        help_text=get_help_text("verzoeken.Verzoek", "geometrie"),
        required=False,
    )
    verzoek_bron = VerzoekBronSerializer(
        source="bron",
        required=False,
        help_text="",  # TODO
    )
    verzoek_betaling = VerzoekBetalingSerializer(
        source="betaling",
        required=False,
        help_text="",  # TODO
    )

    class Meta:
        model = Verzoek
        fields = (
            "url",
            "urn",
            "uuid",
            "verzoek_type",
            "verzoek_type_urn",
            "geometrie",
            "aanvraag_gegevens",
            "bijlagen",
            "is_ingediend_door_partij",
            "is_ingediend_door_betrokkene",
            "heeft_geleid_tot_zaak",
            "authenticatie_context",
            "verzoek_bron",
            "verzoek_betaling",
        )

        extra_kwargs = {
            "uuid": {
                "read_only": True,
            },
            "url": {
                "view_name": "verzoeken:verzoek-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van het verzoek binnen deze API."),
            },
            "urn": {
                "lookup_field": "uuid",
                "help_text": _("De Uniform Resource Name van het Verzoek."),
            },
            "aanvraag_gegevens": {
                "required": True,
            },
        }

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        verzoektype = get_from_serializer_data_or_instance("verzoek_type", attrs, self)
        aanvraag_gegevens = get_from_serializer_data_or_instance(
            "aanvraag_gegevens", attrs, self
        )
        validate_jsonschema(
            instance=aanvraag_gegevens,
            schema=verzoektype.aanvraag_gegevens_schema,
            label="aanvraagGegevens",
        )

        return valid_attrs

    @transaction.atomic
    def create(self, validated_data):
        bron = validated_data.pop("bron", None)
        betaling = validated_data.pop("betaling", None)
        instance = super().create(validated_data)

        if bron:
            VerzoekBron.objects.create(verzoek=instance, **bron)
        if betaling:
            VerzoekBetaling.objects.create(verzoek=instance, **betaling)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        bron = validated_data.pop("bron", None)
        betaling = validated_data.pop("betaling", None)
        instance = super().update(instance, validated_data)
        if bron:
            VerzoekBron.objects.update_or_create(verzoek=instance, defaults={**bron})
        if betaling:
            VerzoekBetaling.objects.update_or_create(
                verzoek=instance, defaults={**betaling}
            )
        return instance
