from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openvtb.components.taken.validators import validate_jsonschema
from openvtb.utils.converters import snake_to_camel_converter
from openvtb.utils.serializers import get_field_value

from ..constants import DEFAULT_VALUTA, VALUTE
from ..models import ExterneTaak


class JsonDataSerializer(serializers.Serializer):
    """
    A serializer mixin that maps declared fields directly to keys inside `instance.data`,
    avoiding the need for `source="data.<field>"` definitions.
    """

    data_field = "data"

    def get_data_dict(self, instance):
        return getattr(instance, self.data_field, {}) or {}

    def to_representation(self, instance):
        data_dict = self.get_data_dict(instance)
        base = {}

        for field_name, field in self.fields.items():
            if field.source == "*":
                base[field_name] = field.to_representation(instance)
                continue
            if hasattr(instance, field_name):
                value = getattr(instance, field_name)
            else:
                value = data_dict.get(snake_to_camel_converter(field_name))
            base[field_name] = field.to_representation(value)
        return base


class ExterneTaakSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExterneTaak
        fields = (
            "uuid",
            "titel",
            "status",
            "startdatum",
            "handelings_perspectief",
            "einddatum_handelings_termijn",
            "datum_herinnering",
            "toelichting",
            "taak_soort",
        )

    def validate(self, attrs):
        data = get_field_value(self, attrs, "data")
        taak_soort = get_field_value(self, attrs, "taak_soort")
        validate_jsonschema(data, taak_soort)
        return super().validate(attrs)


class DoelrekeningSerializer(serializers.Serializer):
    naam = serializers.CharField(
        max_length=200,
        help_text=_("Naam van de ontvanger van de betaling"),
    )
    iban = serializers.CharField(
        help_text=_("IBAN code van de ontvanger"),
    )


class BetaalTaakSerializer(JsonDataSerializer):
    externe_taak = ExterneTaakSerializer(source="*")
    bedrag = serializers.FloatField(
        help_text=_("Bedrag dat betaald moet worden"),
    )
    valuta = serializers.ChoiceField(
        choices=[(v, k) for k, v in VALUTE.items()],
        default=DEFAULT_VALUTA,
        help_text=_("Valuta van de betaling"),
    )
    transactieomschrijving = serializers.CharField(
        max_length=80,
        help_text=_("Omschrijving van de transactie"),
    )
    doelrekening = DoelrekeningSerializer(
        help_text=_("Gegevens van de ontvangende bankrekening"),
    )


class GegevensUitvraagTaakSerializer(JsonDataSerializer):
    externe_taak = ExterneTaakSerializer(source="*")
    uitvraag_link = serializers.URLField(
        help_text=_("Link naar de externe gegevensaanvraag"),
    )
    ontvangen_gegevens = serializers.JSONField(
        required=False,
        default=dict,
        allow_null=True,
        help_text=_("Ontvangen gegevens als key-value object"),
    )


class FormulierTaakSerializer(JsonDataSerializer):
    externe_taak = ExterneTaakSerializer(source="*")
    formulier_definitie = serializers.JSONField(
        required=False,
        default=dict,
        allow_null=True,
        help_text=_("Definitie van het formulier in JSON"),
    )
    ontvangen_gegevens = serializers.JSONField(
        required=False,
        default=dict,
        allow_null=True,
        help_text=_("Ontvangen gegevens als key-value object"),
    )
