from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from ..models import (
    Verzoek,
    VerzoekBetaling,
    VerzoekBron,
    VerzoekType,
    VerzoekTypeVersion,
)

ADRES = {
    "woonplaats": "Amsterdam",
    "postcode": "1000 AB",
    "huisnummer": "12",
    "huisletter": "A",
    "huisnummertoevoeging": "bis",
    "buitenland": {},
}

JSON_SCHEMA = {
    "type": "object",
    "title": "Tree",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "required": ["diameter"],
    "properties": {
        "diameter": {
            "type": "integer",
            "description": "size in cm.",
        },
        "extra": {
            "type": "object",
            "title": "extra",
            "keys": {},
            "additionalProperties": True,
        },
    },
    "additionalProperties": False,
}


class VerzoekTypeFactory(DjangoModelFactory):
    naam = factory.Faker("word")
    toelichting = factory.Faker("sentence", nb_words=8)

    class Meta:
        model = VerzoekType

    @factory.post_generation
    def create_version(obj, create, version, **kwargs):
        if not create:
            return

        if version:
            VerzoekTypeVersionFactory(verzoek_type=obj)


class VerzoekTypeVersionFactory(DjangoModelFactory):
    verzoek_type = factory.SubFactory(VerzoekTypeFactory)
    aanvraag_gegevens_schema = JSON_SCHEMA

    class Meta:
        model = VerzoekTypeVersion


class DataFactory(factory.DictFactory):
    extra = factory.Dict(
        {
            "extra": {
                "bool": False,
                "integer": "100",
            },
        }
    )
    diameter = 10


class VerzoekFactory(DjangoModelFactory):
    verzoek_type = factory.SubFactory(VerzoekTypeFactory)
    aanvraag_gegevens = factory.SubFactory(DataFactory)
    version = 1

    class Meta:
        model = Verzoek

    @factory.post_generation
    def create_details(obj, create, details, **kwargs):
        if not create:
            return

        if details:
            VerzoekBronFactory(verzoek=obj)
            VerzoekBetalingFactory(verzoek=obj)

    class Params:
        authentieke_verwijzing = factory.Trait(
            is_ingediend_door={
                "authentiekeVerwijzing": {
                    "urn": "urn:nld:brp:bsn:111222333",
                }
            }
        )
        niet_authentieke_persoonsgegevens = factory.Trait(
            is_ingediend_door={
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": "Jan",
                    "achternaam": "Jansen",
                    "geboortedatum": "1980-05-15",
                    "emailadres": "jan.jansen@example.com",
                    "telefoonnummer": "+31612345678",
                    "postadres": ADRES,
                    "verblijfsadres": ADRES,
                }
            }
        )
        niet_authentieke_organisatiegegevens = factory.Trait(
            is_ingediend_door={
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": ADRES,
                    "postadres": ADRES,
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                }
            }
        )


class VerzoekBronFactory(DjangoModelFactory):
    verzoek = factory.SubFactory(VerzoekFactory)
    naam = factory.Faker("word")
    kenmerk = factory.Faker("word")

    class Meta:
        model = VerzoekBron


class VerzoekBetalingFactory(DjangoModelFactory):
    verzoek = factory.SubFactory(VerzoekFactory)
    kenmerken = factory.ListFactory()
    bedrag = factory.Faker("pydecimal", left_digits=8, right_digits=2, positive=True)
    voltooid = factory.Faker("pybool")
    transactie_datum = factory.LazyAttribute(lambda _: timezone.now())
    transactie_referentie = factory.Faker("uuid4")

    class Meta:
        model = VerzoekBetaling
