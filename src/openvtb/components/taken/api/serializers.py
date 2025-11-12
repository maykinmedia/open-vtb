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
        group_field="details",
        same_model=False,
    )
    discriminator_field = "taak_soort"

    class Meta:
        model = ExterneTaak
        fields = (
            "url",
            "uuid",
            "titel",
            "status",
            "startdatum",
            "handelings_perspectief",
            "einddatum_handelings_termijn",
            "datum_herinnering",
            "toelichting",
            "taak_soort",
            "details",
        )
        validators = [
            StartBeforeEndValidator("startdatum", "einddatum_handelings_termijn"),
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "details": {"required": True},
            "taak_soort": {"required": True},
            "url": {
                "view_name": "taken:betaaltaken-detail",  # fix TODO
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van deze actor binnen deze API."),
            },
        }

    def _init_taak_soort(self, partial=False):
        """
        Set `taak_soort` with priority:
        1. Use self.taak_soort if already set viewset, raise error if present in initial_data
        2. Use value from initial_data if provided
        3. Use instance value for partial_update, if not provided
        """

        initial_data = getattr(self, "initial_data", None)
        instance = getattr(self, "instance", None)

        if initial_data is None:
            return
        # 1.
        if self.taak_soort:
            if self.discriminator_field in initial_data:
                raise serializers.ValidationError(
                    {
                        self.discriminator_field: _(
                            "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd."
                        )
                    },
                    code="invalid",
                )
            initial_data[self.discriminator_field] = self.taak_soort
            return

        # 2.
        if self.discriminator_field in initial_data:
            self.taak_soort = initial_data[self.discriminator_field]
            return

        # 3.
        if partial and instance is not None:
            initial_data[self.discriminator_field] = instance.taak_soort
            self.taak_soort = instance.taak_soort

    def __init__(self, *args, **kwargs):
        # necessary to pass the partial value in case of PATCH
        for discriminator in self.discriminator.mapping.values():
            discriminator.partial = kwargs.get("partial", False)

        super().__init__(*args, **kwargs)
        if context := kwargs.get("context", {}):
            self.taak_soort = context.get(self.discriminator_field, None)
            self._init_taak_soort(kwargs.get("partial", False))

    def validate(self, attrs):
        details = {
            snake_to_camel_converter(k): v for k, v in attrs.pop("details", {}).items()
        }
        if self.instance and self.instance.details:
            if self.instance.taak_soort == self.taak_soort:
                # update details with instance values
                details = {**self.instance.details, **details}
        validate_jsonschema(details, self.taak_soort)
        attrs["details"] = details
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
