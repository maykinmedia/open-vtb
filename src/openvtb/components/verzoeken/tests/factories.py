import random
import string

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from ..models import (
    Bijlage,
    BijlageType,
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


def get_random_urn() -> str:
    return f"urn:maykin:{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"


class VerzoekTypeFactory(DjangoModelFactory):
    naam = factory.Faker("word")
    omschrijving = factory.Faker("sentence", nb_words=8)

    class Meta:
        model = VerzoekType

    @factory.post_generation
    def create_versie(obj, create, versie, **kwargs):
        if not create:
            return

        if versie:
            VerzoekTypeVersionFactory(verzoek_type=obj)


class VerzoekTypeVersionFactory(DjangoModelFactory):
    verzoek_type = factory.SubFactory(VerzoekTypeFactory)
    aanvraag_gegevens_schema = JSON_SCHEMA

    class Meta:
        model = VerzoekTypeVersion

    @factory.post_generation
    def create_bijlagetype(obj, create, bijlagetype, **kwargs):
        if not create:
            return

        if bijlagetype:
            BijlageTypeFactory(verzoek_type_versie=obj)


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
    initiator = factory.LazyFunction(get_random_urn)
    versie = 1

    class Meta:
        model = Verzoek

    @factory.post_generation
    def create_bijlage(obj, create, bijlage, **kwargs):
        if not create:
            return

        if bijlage:
            BijlageFactory(verzoek=obj)

    @factory.post_generation
    def create_details(obj, create, details, **kwargs):
        if not create:
            return

        if details:
            VerzoekBronFactory(verzoek=obj)
            VerzoekBetalingFactory(verzoek=obj)


class BijlageTypeFactory(DjangoModelFactory):
    class Meta:
        model = BijlageType

    verzoek_type_versie = factory.SubFactory(VerzoekTypeVersionFactory)
    informatie_objecttype = factory.LazyFunction(get_random_urn)
    omschrijving = factory.Faker("sentence", nb_words=4)


class BijlageFactory(DjangoModelFactory):
    class Meta:
        model = Bijlage

    verzoek = factory.SubFactory(VerzoekFactory)
    informatie_object = factory.LazyFunction(get_random_urn)


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
