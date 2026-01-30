import json

from django.utils.translation import gettext_lazy as _

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from djangorestframework_camel_case.util import camel_to_underscore
from rest_framework import serializers
from vng_api_common.polymorphism import Discriminator, PolymorphicSerializer

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.utils import get_json_schema
from openvtb.utils.api_utils import get_from_serializer_data_or_instance
from openvtb.utils.constants import Valuta
from openvtb.utils.serializers import URNModelSerializer
from openvtb.utils.validators import StartBeforeEndValidator, validate_jsonschema

from ..models import ExterneTaak
from .validators import FormulierDefinitieValidator


class DoelrekeningSerializer(serializers.Serializer):
    naam = serializers.CharField(
        required=True,
        max_length=200,
        help_text=_("Naam van de ontvanger van de betaling."),
    )
    code = serializers.CharField(
        required=True,
        max_length=100,
        help_text=_(
            "Een arbitraire code die gebruikt kan worden om de juiste rekening "
            "en/of betaalprovider te kiezen in het systeem dat de taak afhandeld."
        ),
    )
    iban = serializers.CharField(
        required=True,
        help_text=_("IBAN code van de ontvanger."),
    )


class BetaalTaakSerializer(serializers.Serializer):
    bedrag = serializers.CharField(
        required=True,
        help_text=_("Bedrag dat betaald moet worden."),
    )
    valuta = serializers.CharField(
        default=Valuta.EUR,
        help_text=_("Valuta van de betaling."),
    )
    transactieomschrijving = serializers.CharField(
        required=True,
        max_length=80,
        help_text=_("Omschrijving van de transactie."),
    )
    doelrekening = DoelrekeningSerializer(
        required=True,
        help_text=_("Gegevens van de ontvangende bankrekening."),
    )

    def validate_valuta(self, value):
        if value != Valuta.EUR.value:
            raise serializers.ValidationError(
                "Het is niet toegestaan een andere waarde dan {valuta} door te geven.".format(
                    valuta=Valuta.EUR
                )
            )
        return value


class GegevensUitvraagTaakSerializer(serializers.Serializer):
    uitvraag_link = serializers.URLField(
        required=True,
        help_text=_("Link naar de externe gegevensaanvraag."),
    )
    voorinvullen_gegevens = serializers.JSONField(
        default=dict,
        help_text=_(
            "Arbitraire sleutel-waarde gegevens die ingevuld moeten worden in de uitvraag. "
            "De sleutel kan bijvoorbeeld een veldnaam zijn in een formulier, of een veld in een sjabloon."
        ),
    )
    ontvangen_gegevens = serializers.JSONField(
        default=dict,
        help_text=_("Ontvangen gegevens als key-value object."),
    )

    def to_representation(self, instance):
        instance = {camel_to_underscore(k): v for k, v in instance.items()}
        return super().to_representation(instance)


class FormulierTaakSerializer(serializers.Serializer):
    formulier_definitie = serializers.JSONField(
        required=True,
        help_text=_(
            "Definitie van het formulier in JSON. Het formulier moet minimaal het veld 'components' bevatten. "
            "Elke component moet de volgende verplichte velden hebben:\n"
            "- 'label': de naam die weergegeven wordt voor het veld\n"
            "- 'key': de unieke identifier voor het veld\n"
            "- 'type': het type van het veld, bijvoorbeeld 'text', 'number' of 'date'\n \n "
            "Andere velden, zoals 'values', 'format', 'enableTime' of 'fileTypes', zijn optioneel en kunnen gebruikt worden om het gedrag of de weergave van het veld aan te passen."
        ),
    )
    ontvangen_gegevens = serializers.JSONField(
        default=dict,
        help_text=_("Ontvangen gegevens als key-value object."),
    )

    validators = [
        FormulierDefinitieValidator(),
    ]

    def to_representation(self, instance):
        instance = {camel_to_underscore(k): v for k, v in instance.items()}
        return super().to_representation(instance)


class ExterneTaakPolymorphicSerializer(URNModelSerializer, PolymorphicSerializer):
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
            "urn",
            "uuid",
            "titel",
            "status",
            "startdatum",
            "handelings_perspectief",
            "einddatum_handelings_termijn",
            "datum_herinnering",
            "toelichting",
            "is_toegewezen_aan",
            "wordt_behandeld_door",
            "hoort_bij",
            "heeft_betrekking_op",
            "taak_soort",
            "details",
        )
        validators = [
            StartBeforeEndValidator("startdatum", "einddatum_handelings_termijn"),
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "details": {"required": True},
            "taak_soort": {
                "required": True,
                "allow_null": False,
            },
            "url": {
                "view_name": "taken:externetaak-detail",
                "lookup_field": "uuid",
                "help_text": _("De unieke URL van de externe taak deze API."),
            },
            "urn": {
                "lookup_field": "uuid",
                "help_text": _("De Uniform Resource Name van de externe taak."),
            },
        }

    def _init_taak_soort(self, taak_soort, partial=False):
        """
        Initialize `taak_soort`:

        - If `taak_soort` is already set:
            - if it also appears in `initial_data`, raise a ValidationError
            - Otherwise, insert it into `initial_data` as default

        - If `partial=True` and is not passed to the initial data:
            - Add `taak_soort` value into `initial_data`
        """

        initial_data = getattr(self, "initial_data", None)
        instance = getattr(self, "instance", None)

        if initial_data is None:
            return

        if taak_soort:
            if self.discriminator_field in initial_data:
                raise serializers.ValidationError(
                    {
                        self.discriminator_field: _(
                            "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd."
                        )
                    },
                    code="invalid",
                )
            initial_data[self.discriminator_field] = taak_soort
            return

        if partial and instance and self.discriminator_field not in initial_data:
            initial_data[self.discriminator_field] = instance.taak_soort
            return

    def __init__(self, *args, **kwargs):
        partial = kwargs.get("partial", False)
        # partial pass for PATCH the content of the details
        for discriminator in self.discriminator.mapping.values():
            discriminator.partial = partial

        super().__init__(*args, **kwargs)
        if context := kwargs.get("context", {}):
            taak_soort = context.get(self.discriminator_field, None)
            self._init_taak_soort(taak_soort, partial)

    def validate(self, attrs):
        renderer = CamelCaseJSONRenderer()
        details = json.loads(renderer.render(attrs.pop("details", {})))
        taak_soort = get_from_serializer_data_or_instance(
            self.discriminator_field, attrs, self
        )
        if self.instance and self.instance.taak_soort == taak_soort:
            # update details only for the same taak_soort
            details = {**self.instance.details, **details}
        validate_jsonschema(
            instance=details,
            label="details",
            schema=get_json_schema(taak_soort),
        )
        attrs["details"] = details
        return super().validate(attrs)
