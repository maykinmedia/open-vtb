import random
import uuid

import factory
from factory.django import DjangoModelFactory

from ..models import Verzoek, VerzoekType, VerzoekTypeVersion

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
    uuid = factory.LazyFunction(uuid.uuid4)
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
            "string": "True",
            "bool": False,
            "integer": random.randrange(1, 10_000),
        }
    )
    diameter = factory.LazyAttribute(lambda x: random.randrange(1, 10_000))


class VerzoekFactory(DjangoModelFactory):
    verzoek_type = factory.SubFactory(VerzoekTypeFactory)
    aanvraag_gegevens = factory.SubFactory(DataFactory)

    class Meta:
        model = Verzoek
