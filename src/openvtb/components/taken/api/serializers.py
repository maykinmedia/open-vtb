from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from vng_api_common.polymorphism import Discriminator, PolymorphicSerializer

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.validators import validate_jsonschema
from openvtb.utils.converters import camel_to_snake_converter, snake_to_camel_converter
from openvtb.utils.validators import StartBeforeEndValidator

from ..constants import DEFAULT_VALUTA
from ..models import ExterneTaak


class DoelrekeningSerializer(serializers.Serializer):
    naam = serializers.CharField(
        required=True,
        max_length=200,
        help_text=_("Naam van de ontvanger van de betaling"),
    )
    iban = serializers.CharField(
        required=True,
        help_text=_("IBAN code van de ontvanger"),
    )


class BetaalTaakSerializer(serializers.Serializer):
    bedrag = serializers.CharField(
        required=True,
        help_text=_("Bedrag dat betaald moet worden"),
    )
    valuta = serializers.CharField(
        default=DEFAULT_VALUTA,
        help_text=_("Valuta van de betaling"),
    )
    transactieomschrijving = serializers.CharField(
        required=True,
        max_length=80,
        help_text=_("Omschrijving van de transactie"),
    )
    doelrekening = DoelrekeningSerializer(
        required=True,
        help_text=_("Gegevens van de ontvangende bankrekening"),
    )

    def validate_valuta(self, value):
        if value != DEFAULT_VALUTA:
            raise serializers.ValidationError(
                "Het is niet toegestaan een andere waarde dan {valuta} door te geven.".format(
                    valuta=DEFAULT_VALUTA
                )
            )
        return value


class GegevensUitvraagTaakSerializer(serializers.Serializer):
    uitvraag_link = serializers.URLField(
        required=True,
        help_text=_("Link naar de externe gegevensaanvraag"),
    )
    ontvangen_gegevens = serializers.JSONField(
        default=dict,
        help_text=_("Ontvangen gegevens als key-value object"),
    )

    def to_representation(self, instance):
        instance = {camel_to_snake_converter(k): v for k, v in instance.items()}
        return super().to_representation(instance)


class FormulierTaakSerializer(serializers.Serializer):
    formulier_definitie = serializers.JSONField(
        required=True,
        help_text=_("Definitie van het formulier in JSON"),
    )
    ontvangen_gegevens = serializers.JSONField(
        default=dict,
        help_text=_("Ontvangen gegevens als key-value object"),
    )

    def to_representation(self, instance):
        instance = {camel_to_snake_converter(k): v for k, v in instance.items()}
        return super().to_representation(instance)


class ExterneTaakPolymorphicSerializer(PolymorphicSerializer):
    discriminator = Discriminator(
        discriminator_field="taak_soort",
        mapping={
            SoortTaak.BETAALTAAK: BetaalTaakSerializer(),
            SoortTaak.GEGEVENSUITVRAAGTAAK: GegevensUitvraagTaakSerializer(),
            SoortTaak.FORMULIERTAAK: FormulierTaakSerializer(),
        },
        group_field="data",
        same_model=False,
    )
    data = serializers.JSONField(required=True)

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
            "data",
        )
        validators = [
            StartBeforeEndValidator("startdatum", "einddatum_handelings_termijn"),
        ]

    def _init_taak_soort(self):
        initial_data = getattr(self, "initial_data", None)
        if initial_data is not None:
            if "taak_soort" in initial_data:
                raise serializers.ValidationError(
                    {
                        "taakSoort": _(
                            "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd."
                        )
                    },
                    code="invalid",
                )
            self.initial_data["taak_soort"] = self.taak_soort

    def __init__(self, *args, **kwargs):
        # necessary to pass the partial value in case of PATCH
        for discriminator in self.discriminator.mapping.values():
            discriminator.partial = kwargs.get("partial", False)

        self.view = kwargs.get("context", {}).get("view", None)
        if not self.view:
            raise ValidationError(
                _("View required for discriminator value"), code="required"
            )

        self.taak_soort = self.view.taak_soort
        super().__init__(*args, **kwargs)
        self._init_taak_soort()

    def validate(self, attrs):
        attrs["taak_soort"] = self.taak_soort

        data = {
            snake_to_camel_converter(k): v for k, v in attrs.pop("data", {}).items()
        }
        if self.instance and getattr(self.instance, "data", None):
            # update data with instance values
            data = {**self.instance.data, **data}

        validate_jsonschema(data, self.taak_soort)
        attrs["data"] = data
        return super().validate(attrs)


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
