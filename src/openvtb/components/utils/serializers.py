import json

from django.utils.translation import gettext_lazy as _

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import serializers

from openvtb.utils.api_mixins import CamelToUnderscoreMixin
from openvtb.utils.serializers import (
    URNField,
)


class AuthentiekeVerwijzingSerializer(serializers.Serializer):
    urn = URNField(
        required=True,
        help_text=_("Authentieke Referentie URN"),
    )


class NietAuthentiekePersoonsgegevensSerializer(
    CamelToUnderscoreMixin, serializers.Serializer
):
    voornaam = serializers.CharField(
        max_length=100,
        required=True,
        help_text="De voornaam van de persoon.",
    )
    achternaam = serializers.CharField(
        max_length=100,
        required=True,
        help_text="De achternaam van de persoon.",
    )
    geboortedatum = serializers.DateField(
        required=True,
        help_text="De geboortedatum van de persoon in het formaat YYYY-MM-DD.",
    )
    emailadres = serializers.EmailField(
        required=True,
        help_text="Het e-mailadres van de persoon.",
    )
    telefoonnummer = serializers.CharField(
        max_length=20,
        required=True,
        help_text="Het telefoonnummer van de persoon.",
    )
    postadres = serializers.JSONField(
        default=dict,
        help_text="Het postadres van de persoon.",
    )

    verblijfsadres = serializers.JSONField(
        default=dict,
        help_text="Het huidige verblijfsadres van de persoon.",
    )


class NietAuthentiekeOrganisatiegegevensSerializer(
    CamelToUnderscoreMixin, serializers.Serializer
):
    statutaire_naam = serializers.CharField(
        max_length=200,
        required=True,
        help_text="De officiële statutaire naam van de organisatie.",
    )
    bezoekadres = serializers.JSONField(
        default=dict,
        help_text="Het bezoekadres van de organisatie.",
    )
    postadres = serializers.JSONField(
        default=dict,
        help_text="Het postadres van de organisatie.",
    )
    emailadres = serializers.EmailField(
        required=True,
        help_text="Het e-mailadres van de organisatie.",
    )
    telefoonnummer = serializers.CharField(
        max_length=20,
        required=True,
        help_text="Het telefoonnummer van de organisatie.",
    )


class IsIngediendDoorSerializer(CamelToUnderscoreMixin, serializers.Serializer):
    authentieke_verwijzing = AuthentiekeVerwijzingSerializer(
        required=False,
        allow_null=True,
        help_text="Object dat een authentieke verwijzing vertegenwoordigt. "
        "URN van een NATUURLIJK PERSOON of NIET-NATUURLIJK PERSOON. "
        "Bijvoorbeeld: "
        "`urn:nld:brp.bsn:111222333`, `urn:nld.hr.kvknummer:444555666` of `urn:nld.hr.kvknummer:444555666:vestigingsnummer:777888999`",
    )
    niet_authentieke_persoonsgegevens = NietAuthentiekePersoonsgegevensSerializer(
        required=False,
        allow_null=True,
        help_text="Object met niet-authentieke persoonsgegevens.",
    )
    niet_authentieke_organisatiegegevens = NietAuthentiekeOrganisatiegegevensSerializer(
        required=False,
        allow_null=True,
        help_text="Object met niet-authentieke organisatiegegevens.",
    )

    def validate(self, data):
        renderer = CamelCaseJSONRenderer()
        data = json.loads(renderer.render(data))
        return data
