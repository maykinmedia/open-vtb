from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openvtb.utils.serializers import (
    URNModelSerializer,
)

from ..models import Bericht, Bijlage


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
            "is_bericht_type_bijlage",
        )
        extra_kwargs = {
            "is_bericht_type_bijlage": {"default": False},
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
            "handelings_perspectief",
            "einddatum_handelings_termijn",
            "mijn_overheid_berichtenbox",
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
