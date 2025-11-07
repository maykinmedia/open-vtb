from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.validators import validate_jsonschema
from openvtb.utils.converters import snake_to_camel_converter

from ..constants import DEFAULT_VALUTA, VALUTE
from ..models import ExterneTaak


class SoortTaakSerializerMixin(serializers.Serializer):
    """
    Mixin for taak_soort serializers that automatically maps declared serializer fields
    to keys inside the `data` JSONField of an ExterneTaak instance.
    """

    data_field = "data"
    taak_soort = None

    def get_data_dict(self, instance):
        return getattr(instance, self.data_field, {}) or {}

    def to_representation(self, instance):
        """
        Maps declared fields directly to keys inside `instance.data`,
        avoiding the need for `source="data.<field>"` definitions.
        """

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
            base[field_name] = (
                field.to_representation(value) if value is not None else None
            )
        return base

    def validate(self, attrs):
        if attrs.pop("taak_soort", None):
            raise serializers.ValidationError(
                {
                    "externeTaak.taakSoort": _(
                        "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd."
                    )
                },
                code="invalid",
            )
        fields = getattr(self.Meta, "task_fields", [])
        data = {k: attrs.pop(k) for k in fields if k in attrs}
        attrs["taak_soort"] = self.taak_soort
        if self.instance and getattr(self.instance, "data", None):
            # update data with instance values
            data = {**self.instance.data, **data}

        attrs["data"] = data
        validate_jsonschema(data, self.taak_soort)
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        return ExterneTaak.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        ExterneTaak.objects.filter(pk=instance.pk).update(**validated_data)
        instance.refresh_from_db()
        return instance


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
        extra_kwargs = {
            "taak_soort": {
                "required": False,
            },
        }


class DoelrekeningSerializer(serializers.Serializer):
    naam = serializers.CharField(
        max_length=200,
        help_text=_("Naam van de ontvanger van de betaling"),
    )
    iban = serializers.CharField(
        help_text=_("IBAN code van de ontvanger"),
    )


class BetaalTaakSerializer(SoortTaakSerializerMixin):
    externe_taak = ExterneTaakSerializer(source="*")
    bedrag = serializers.CharField(
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

    taak_soort = SoortTaak.BETAALTAAK

    class Meta:
        task_fields = ["bedrag", "valuta", "transactieomschrijving", "doelrekening"]


class GegevensUitvraagTaakSerializer(SoortTaakSerializerMixin):
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

    taak_soort = SoortTaak.GEGEVENSUITVRAAGTAAK

    class Meta:
        task_fields = ["uitvraag_link", "ontvangen_gegevens"]


class FormulierTaakSerializer(SoortTaakSerializerMixin):
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

    taak_soort = SoortTaak.FORMULIERTAAK

    class Meta:
        task_fields = ["formulier_definitie", "ontvangen_gegevens"]
