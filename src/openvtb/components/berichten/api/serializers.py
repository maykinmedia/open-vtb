from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from vng_api_common.serializers import CachedHyperlinkedRelatedField
from vng_api_common.utils import get_help_text

from openvtb.utils.serializers import (
    URNField,
    URNModelSerializer,
    URNRelatedField,
)
from openvtb.utils.validators import IsImmutableValidator

from ..models import Bericht, BerichtType, Bijlage, BijlageType


class IsGerelateerdAanSerializer(serializers.Serializer):
    urn = URNField(
        required=True,
        help_text=_(
            "URN naar de ZAAK of het PRODUCT. "
            "Bijvoorbeeld: `urn:nld:gemeenteutrecht:zaak:zaaknummer:000350165` "
            "of `urn:nld:gemeenteutrecht:product:uuid:717815f6-1939-4fd2-93f0-83d25bad154e`."
        ),
    )


class BerichtGeopendOpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bericht
        fields = ["geopend_op"]


class BijlageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bijlage
        fields = (
            "informatie_object",
            "omschrijving",
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


class BerichtSerializer(URNModelSerializer, serializers.ModelSerializer):
    bijlagen = BijlageSerializer(
        required=False,
        many=True,
        help_text=_(
            "Lijst van bijlagen bij het bericht. Let op; In het geval dat dit bericht naar "
            "de Mijn Overheid Berichtenbox moet, moet rekening gehouden worden met "
            "de requirements van Logius in haar technische aansluithandleiding."
        ),
    )
    is_gerelateerd_aan = serializers.ListSerializer(
        child=IsGerelateerdAanSerializer(),
        required=False,
        help_text=get_help_text("berichten.Bericht", "is_gerelateerd_aan"),
    )
    bericht_type = CachedHyperlinkedRelatedField(
        view_name="berichten:berichttype-detail",
        lookup_field="uuid",
        required=True,
        queryset=BerichtType.objects.all(),
        validators=[IsImmutableValidator()],
        help_text=get_help_text("berichten.Bericht", "bericht_type"),
    )
    bericht_type_urn = URNRelatedField(
        lookup_field="uuid",
        source="bericht_type",
        urn_resource="berichttype",
        read_only=True,
        help_text=get_help_text("berichten.Bericht", "bericht_type") + _("URN field"),
    )

    class Meta:
        model = Bericht
        fields = (
            "url",
            "urn",
            "uuid",
            "onderwerp",
            "bericht_tekst",
            "publicatiedatum",
            "referentie",
            "ontvanger",
            "geopend_op",
            "bericht_type",
            "bericht_type_urn",
            "is_gerelateerd_aan",
            "einddatum_handelings_termijn",
            "bijlagen",
        )
        extra_kwargs = {
            "uuid": {"read_only": True},
            "url": {
                "view_name": "berichten:bericht-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van het Bericht binnen deze API."),
            },
            "urn": {
                "lookup_field": "uuid",
                "help_text": _("De Uniform Resource Name van het Bericht."),
            },
        }

    @transaction.atomic
    def create(self, validated_data):
        bijlagen = validated_data.pop("bijlagen", None)
        instance = super().create(validated_data)

        if bijlagen:
            try:
                objs = [Bijlage(bericht=instance, **data) for data in bijlagen]
                Bijlage.objects.bulk_create(objs)
            except IntegrityError:
                raise serializers.ValidationError(
                    {
                        "bijlagen": "Bijlage with the specified informatieObject already exists."
                    },
                    code="unique",
                )
        return instance


class BerichtTypeSerializer(URNModelSerializer, serializers.ModelSerializer):
    bijlage_typen = BijlageTypeSerializer(
        required=False,
        many=True,
        help_text=_("Lijst met bijlagenTypen die aan deze bron zijn gekoppeld."),
    )

    class Meta:
        model = BerichtType
        fields = (
            "url",
            "urn",
            "uuid",
            "bijlage_typen",
            "handelings_perspectief",
            "mijn_overheid_berichtenbox",
            "mijn_overheid_berichtenbox_type",
            "verantwoordelijke_organisatie",
        )
        extra_kwargs = {
            "uuid": {"read_only": True},
            "url": {
                "view_name": "berichten:berichttype-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van het BerichtType binnen deze API."),
            },
            "urn": {
                "lookup_field": "uuid",
                "help_text": _("De Uniform Resource Name van het Bericht."),
            },
        }

    @transaction.atomic
    def create(self, validated_data):
        bijlage_typen = validated_data.pop("bijlage_typen", None)
        instance = super().create(validated_data)

        if bijlage_typen:
            try:
                objs = [
                    BijlageType(bericht_type=instance, **data) for data in bijlage_typen
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
                    bericht_type=instance,
                    informatie_objecttype=bijlage_type["informatie_objecttype"],
                    defaults={**bijlage_type},
                )
        return instance
