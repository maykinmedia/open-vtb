import random
import uuid

import factory
from factory.django import DjangoModelFactory

from ..models import VerzoekType, VerzoekTypeVersion


class VerzoekTypeFactory(DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Faker("word")
    toelichting = factory.Faker("sentence", nb_words=8)

    class Meta:
        model = VerzoekType


class VerzoekTypeVersionFactory(DjangoModelFactory):
    verzoek_type = factory.SubFactory(VerzoekTypeFactory)
    aanvraag_gegevens_schema = {
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

    class Meta:
        model = VerzoekTypeVersion


class DataFactory(factory.DictFactory):
    extra = factory.Dict(
        {
            "string": "True",
            "bool": False,
            "integer": random.randrange(1, 10_000),
        }
    )
    diameter = factory.LazyAttribute(lambda x: random.randrange(1, 10_000))


class Verzoek(DjangoModelFactory):
    verzoek_type = factory.SubFactory(VerzoekTypeFactory)
    aanvraag_gegevens = factory.SubFactory(DataFactory)
