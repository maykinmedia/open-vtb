from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import VerzoekTypeVersion
from .factories import (
    JSON_SCHEMA,
    VerzoekFactory,
    VerzoekTypeFactory,
)


class ValidateVerzoekTypeSchemaTestCase(TestCase):
    def test_valid_schema(self):
        verzoek_type = VerzoekTypeFactory.create(create_version=True)
        self.assertEqual(verzoek_type.last_version.version, 1)
        self.assertEqual(
            verzoek_type.last_version.aanvraag_gegevens_schema,
            JSON_SCHEMA,  # default from factories
        )

    def test_invalid_schema(self):
        invalid_schemas = [
            # Invalid type
            {"type": "unknown_type"},
            # Property with invalid schema
            {"type": "object", "properties": {"name": {"type": "invalid_type"}}},
            # 'required' property that does not exist
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["age"],  # 'age' is not defined in properties
            },
            # Schema with an invalid key
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "unknown_keyword": True,  # key not allowed by JSON Schema
            },
            # Empty schema invalid for declared type
            {
                "type": "array",
                "items": {"type": "unknown_type"},  # invalid type in items
            },
        ]

        verzoek_type = VerzoekTypeFactory.create()
        for schema in invalid_schemas:
            with self.assertRaises(ValidationError):
                instance = VerzoekTypeVersion(
                    verzoek_type=verzoek_type, aanvraag_gegevens_schema=schema
                )
                instance.full_clean()


class ValidateVerzoekSchemaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.verzoek_type = VerzoekTypeFactory.create(create_version=True)

    def test_valid_schema(self):
        # default schema from factory
        self.assertEqual(self.verzoek_type.last_version.version, 1)
        self.assertEqual(
            self.verzoek_type.last_version.aanvraag_gegevens_schema,
            JSON_SCHEMA,
        )
        self.verzoek = VerzoekFactory.create(
            verzoek_type=self.verzoek_type, aanvraag_gegevens={"diameter": 1}
        )
        self.verzoek.full_clean()

    def test_without_verzoek_type_schema(self):
        self.assertEqual(self.verzoek_type.last_version.version, 1)
        self.assertEqual(
            self.verzoek_type.last_version.aanvraag_gegevens_schema, JSON_SCHEMA
        )
        with self.assertRaises(ValidationError) as error:
            self.verzoek = VerzoekFactory.create(aanvraag_gegevens={"diameter": 1})
            self.verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {"verzoek_type": ["Onbekend VerzoekType schema: geen schema beschikbaar."]},
        )

    def test_invalid_schema(self):
        self.assertEqual(self.verzoek_type.last_version.version, 1)
        self.assertEqual(
            self.verzoek_type.last_version.aanvraag_gegevens_schema,
            JSON_SCHEMA,
        )
        with self.assertRaises(ValidationError) as error:
            self.verzoek = VerzoekFactory.create(
                verzoek_type=self.verzoek_type,
                aanvraag_gegevens={"test": 1},  # invalid key
            )
            self.verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "aanvraag_gegevens": [
                    "{'aanvraag_gegevens': [\"'diameter' is a required property\"]}"
                ]
            },
        )
        with self.assertRaises(ValidationError) as error:
            self.verzoek = VerzoekFactory.create(
                verzoek_type=self.verzoek_type,
                aanvraag_gegevens={"diameter": "test"},  # string
            )
            self.verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "aanvraag_gegevens": [
                    "{'aanvraag_gegevens.diameter': [\"'test' is not of type 'integer'\"]}"
                ]
            },
        )
