from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from vng_api_common.serializers import CachedHyperlinkedRelatedField
from vng_api_common.utils import get_help_text

from openvtb.components.utils.serializers import IsIngediendDoorSerializer
from openvtb.components.utils.validators import IsIngediendDoorValidator
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


class BijlageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BijlageType
        fields = (
            "informatie_objecttype",
            "omschrijving",
        )
        extra_kwargs = {
            "informatie_objecttype": {"required": True, "validators": []},
        }


class VerzoekTypeVersionSerializer(NestedHyperlinkedModelSerializer):
    """
    Serializer for a specific version of a ``VerzoekType``.

    Used in nested endpoints under ``VerzoekType`` and exposes
    version fields and a read-only URN reference to the related ``VerzoekType``.
    """

    parent_lookup_kwargs = {"verzoektype_uuid": "verzoek_type__uuid"}

    bijlage_typen = BijlageTypeSerializer(
        required=False,
        many=True,
        help_text=_("Lijst met bijlagen typen die aan deze bron zijn gekoppeld."),
    )

    class Meta:
        model = VerzoekTypeVersion
        fields = (
            "url",
            "version",
            "verzoek_type",
            "bijlage_typen",
            "status",
            "aanvraag_gegevens_schema",
            "aangemaakt_op",
            "gewijzigd_op",
            "begin_geldigheid",
            "einde_geldigheid",
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
            "aangemaakt_op": {"read_only": True},
            "gewijzigd_op": {"read_only": True},
            "begin_geldigheid": {"read_only": True},
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

    def validate_bijlage_typen(self, value):
        """
        Ensure that each nested object has the 'informatie_objecttype' field filled in.
        """
        for obj in value:
            if not obj.get("informatie_objecttype"):
                raise serializers.ValidationError(
                    _("bijlageType must have a informatieObjecttype."),
                    code="required",
                )
        return value

    @transaction.atomic
    def create(self, validated_data):
        bijlage_typen = validated_data.pop("bijlage_typen", None)
        instance = super().create(validated_data)

        if bijlage_typen:
            try:
                objs = [
                    BijlageType(verzoek_type_version=instance, **data)
                    for data in bijlage_typen
                ]
                BijlageType.objects.bulk_create(objs)
            except IntegrityError:
                raise serializers.ValidationError(
                    {
                        "bijlageTypen": "BijlageType with the specified informatieObjecttype already exists."
                    },
                    code="unique",
                )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        bijlage_typen = validated_data.pop("bijlage_typen", None)
        instance = super().update(instance, validated_data)
        if bijlage_typen:
            for bijlage_type in bijlage_typen:
                BijlageType.objects.update_or_create(
                    verzoek_type_version=instance,
                    informatie_objecttype=bijlage_type["informatie_objecttype"],
                    defaults={**bijlage_type},
                )
        return instance


class BijlageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bijlage
        fields = (
            "informatie_object",
            "toelichting",
        )
        extra_kwargs = {
            "informatie_object": {"required": True, "validators": []},
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
    """
    Read-only serializer for a ``VerzoekTypeVersion``.

    Exposes minimal version information for nested endpoints.
    """

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
                    "De unieke URL van deze VerzoekType versie binnen deze API."
                ),
            },
        }


class VerzoekTypeSerializer(URNModelSerializer, serializers.ModelSerializer):
    versions = VerzoekTypeVersionReadOnlySerializer(
        read_only=True,
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
        help_text=_("Verzoek tot betaling gekoppeld aan deze resource."),  # TODO check
    )
    bijlagen = BijlageSerializer(
        required=False,
        many=True,
        help_text=_(
            "Lijst met bijlagen die aan deze bron zijn gekoppeld."
        ),  # TODO check
    )
    is_ingediend_door = IsIngediendDoorSerializer(
        required=False,
        help_text=(
            "Gegevens over wie het verzoek heeft ingediend. "
            "Let op: slechts ÉÉN van de drie mag aanwezig zijn! "
            "Keuzes: **authentiekeVerwijzing**, **nietAuthentiekePersoonsgegevens** of **nietAuthentiekeOrganisatiegegevens**."
        ),
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
            "is_ingediend_door",
            "is_gerelateerd_aan",
            "kanaal",
            "authenticatie_context",
            "informatie_object",
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
        IsIngediendDoorValidator("is_ingediend_door"),
    ]

    def validate_bijlagen(self, value):
        """
        Ensure that each nested object has the 'informatie_object' field filled in.
        """
        for obj in value:
            if not obj.get("informatie_object"):
                raise serializers.ValidationError(
                    _("bijlage must have a informatieObject."),
                    code="required",
                )
        return value

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
            try:
                objs = [Bijlage(verzoek=instance, **data) for data in bijlagen]
                Bijlage.objects.bulk_create(objs)
            except IntegrityError:
                raise serializers.ValidationError(
                    {
                        "bijlagen": "Bijlage with the specified informatieObject already exists."
                    },
                    code="unique",
                )
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
                Bijlage.objects.update_or_create(
                    verzoek=instance,
                    informatie_object=bijlage["informatie_object"],
                    defaults={**bijlage},
                )
        return instance
