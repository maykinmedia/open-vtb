from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from vng_api_common.serializers import CachedHyperlinkedRelatedField
from vng_api_common.utils import get_help_text

from openvtb.utils.serializers import (
    URNModelSerializer,
    URNRelatedField,
)

from ..models import (
    Bijlage,
    BijlageType,
    Verzoek,
    VerzoekBetaling,
    VerzoekBron,
    VerzoekType,
    VerzoekTypeVersion,
)
from .validators import (
    AanvraagGegevensValidator,
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
                    "De unieke URL van deze VerzoekType versie binnen deze API."
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


class BijlageTypeSerializer(URNModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = BijlageType
        fields = (
            "urn",
            "url",
            "omschrijving",
        )

        extra_kwargs = {
            "urn": {
                "lookup_field": "uuid",
                "urn_component": "verzoeken",
                "urn_resource": "bijlagetype",
                "help_text": _("De Uniform Resource Name van het bijlagetype."),
            },
        }


class BijlageSerializer(URNModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = Bijlage
        fields = (
            "urn",
            "url",
            "omschrijving",
        )

        extra_kwargs = {
            "urn": {
                "lookup_field": "uuid",
                "urn_component": "verzoeken",
                "urn_resource": "bijlage",
                "help_text": _("De Uniform Resource Name van het bijlage."),
            },
        }


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


class VerzoekTypeVersionReadOnlySerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {"verzoektype_uuid": "verzoek_type__uuid"}

    class Meta:
        model = VerzoekTypeVersion
        fields = (
            "url",
            "version",
            "status",
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
        }


class VerzoekTypeSerializer(URNModelSerializer, serializers.ModelSerializer):
    versions = VerzoekTypeVersionReadOnlySerializer(
        read_only=True,
        many=True,
        help_text="",  # TODO
    )

    bijlage_typen = BijlageTypeSerializer(
        required=False,
        many=True,
        help_text="",  # TODO
    )

    class Meta:
        model = VerzoekType
        fields = (
            "url",
            "urn",
            "uuid",
            "versions",
            "naam",
            "toelichting",
            "opvolging",
            "bijlage_typen",
        )

        extra_kwargs = {
            "uuid": {"read_only": True},
            "url": {
                "view_name": "verzoeken:verzoektype-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van het VerzoekType binnen deze API."),
            },
            "urn": {
                "lookup_field": "uuid",
                "help_text": _("De Uniform Resource Name van het VerzoekType."),
            },
        }

    @transaction.atomic
    def create(self, validated_data):
        bijlage_typen = validated_data.pop("bijlage_typen", None)
        instance = super().create(validated_data)

        if bijlage_typen:
            for bijlage_type in bijlage_typen:
                BijlageType.objects.create(verzoek_type=instance, **bijlage_type)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        bijlage_typen = validated_data.pop("bijlage_typen", None)
        instance = super().update(instance, validated_data)

        if bijlage_typen:
            for bijlage_type in bijlage_typen:
                BijlageType.objects.update_or_create(
                    verzoek_type=instance, defaults={**bijlage_type}
                )
        return instance


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
    bijlagen = BijlageSerializer(
        required=False,
        many=True,
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
            "version",
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

    validators = [
        AanvraagGegevensValidator(),
    ]

    @transaction.atomic
    def create(self, validated_data):
        bron = validated_data.pop("bron", None)
        betaling = validated_data.pop("betaling", None)
        bijlagen = validated_data.pop("bijlagen", None)
        instance = super().create(validated_data)

        if bron:
            VerzoekBron.objects.create(verzoek=instance, **bron)
        if betaling:
            VerzoekBetaling.objects.create(verzoek=instance, **betaling)
        if bijlagen:
            for bijlage in bijlagen:
                Bijlage.objects.create(verzoek=instance, **bijlage)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        bron = validated_data.pop("bron", None)
        betaling = validated_data.pop("betaling", None)
        bijlagen = validated_data.pop("bijlagen", None)
        instance = super().update(instance, validated_data)
        if bron:
            VerzoekBron.objects.update_or_create(verzoek=instance, defaults={**bron})
        if betaling:
            VerzoekBetaling.objects.update_or_create(
                verzoek=instance, defaults={**betaling}
            )
        if bijlagen:
            for bijlage in bijlagen:
                Bijlage.objects.update_or_create(verzoek=instance, defaults={**bijlage})
        return instance
