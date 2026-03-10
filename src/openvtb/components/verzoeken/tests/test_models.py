from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Verzoek, VerzoekType, VerzoekTypeVersion
from .factories import (
    JSON_SCHEMA,
    VerzoekFactory,
    VerzoekTypeFactory,
)


class ValidateVerzoekTypeSchemaTestCase(TestCase):
    def test_valid_schema(self):
        verzoek_type = VerzoekTypeFactory.create(create_versie=True)
        self.assertEqual(verzoek_type.last_versie.versie, 1)
        self.assertEqual(
            verzoek_type.last_versie.aanvraag_gegevens_schema,
            JSON_SCHEMA,  # default from factories
        )

    def test_required_fields(self):
        with self.assertRaises(ValidationError) as error:
            instance = VerzoekType()
            instance.full_clean()

        self.assertEqual(
            error.exception.message_dict,
            {"naam": ["Dit veld kan niet leeg zijn"]},
        )

        with self.assertRaises(ValidationError) as error:
            instance = VerzoekTypeVersion()
            instance.full_clean()

        self.assertEqual(
            error.exception.message_dict,
            {
                "verzoek_type": ["Dit veld mag niet leeg zijn."],
                "versie": ["Dit veld mag niet leeg zijn."],
                "einde_geldigheid": ["Dit veld kan niet leeg zijn"],
                "aanvraag_gegevens_schema": ["Dit veld kan niet leeg zijn"],
            },
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
        self.verzoek_type = VerzoekTypeFactory.create(create_versie=True)

    def test_valid_schema(self):
        # default schema from factory
        self.assertEqual(self.verzoek_type.last_versie.versie, 1)
        self.assertEqual(
            self.verzoek_type.last_versie.aanvraag_gegevens_schema,
            JSON_SCHEMA,
        )
        self.verzoek = VerzoekFactory.create(
            verzoek_type=self.verzoek_type, aanvraag_gegevens={"diameter": 1}
        )
        self.verzoek.full_clean()

    def test_required_fields(self):
        with self.assertRaises(ValidationError) as error:
            instance = Verzoek()
            instance.full_clean()

        self.assertEqual(
            error.exception.message_dict,
            {
                "verzoek_type": ["Dit veld mag niet leeg zijn."],
                "aanvraag_gegevens": ["Dit veld kan niet leeg zijn"],
            },
        )

    def test_without_verzoek_type_schema(self):
        with self.assertRaises(ValidationError) as error:
            self.verzoek = VerzoekFactory.create(aanvraag_gegevens={"diameter": 1})
            self.verzoek.full_clean()

        self.assertFalse(self.verzoek.verzoek_type.versies.exists())
        self.assertEqual(
            error.exception.message_dict,
            {
                "versie": [
                    "Onbekend VerzoekType schema versie: geen schema beschikbaar."
                ]
            },
        )

    def test_invalid_schema(self):
        self.assertEqual(self.verzoek_type.last_versie.versie, 1)
        self.assertEqual(
            self.verzoek_type.last_versie.aanvraag_gegevens_schema,
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
