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

    def test_schema_format_checker(self):
        versie = self.verzoek_type.last_versie
        versie.aanvraag_gegevens_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["open", "closed"]},
                "description": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "created_by": {"type": "string"},
                        "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    "required": ["created_by"],
                    "additionalProperties": False,
                },
                "color": {"type": "string", "format": "color"},
                "date": {"type": "string", "format": "date"},
                "date-time": {"type": "string", "format": "date-time"},
                "duration": {"type": "string", "format": "duration"},
                "time": {"type": "string", "format": "time"},
                "email": {"type": "string", "format": "email"},
                "hostname": {"type": "string", "format": "hostname"},
                "idn-hostname": {"type": "string", "format": "idn-hostname"},
                "ipv4": {"type": "string", "format": "ipv4"},
                "ipv6": {"type": "string", "format": "ipv6"},
                "json-pointer": {"type": "string", "format": "json-pointer"},
                "relative-json-pointer": {
                    "type": "string",
                    "format": "relative-json-pointer",
                },
                "regex": {"type": "string", "format": "regex"},
                "uri": {"type": "string", "format": "uri"},
                "uri-reference": {"type": "string", "format": "uri-reference"},
                "uri-template": {"type": "string", "format": "uri-template"},
                "uuid": {"type": "string", "format": "uuid"},
            },
            "additionalProperties": False,
        }
        versie.save()

        self.verzoek = VerzoekFactory.create(
            verzoek_type=self.verzoek_type,
            aanvraag_gegevens={
                "status": "open",
                "description": "Valid request",
                "tags": ["test", "example"],
                "metadata": {"created_by": "user1", "priority": 3},
                "color": "#ff0000",
                "date": "2026-03-16",
                "date-time": "2026-03-16T12:34:56Z",
                "duration": "P3Y6M4DT12H30M5S",
                "time": "12:34:56Z",
                "email": "test@example.com",
                "hostname": "example.com",
                "idn-hostname": "xn--exmple-cua.com",
                "ipv4": "192.168.1.1",
                "ipv6": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                "json-pointer": "/foo/bar",
                "relative-json-pointer": "0/foo",
                "regex": "^[a-z]+$",
                "uri": "https://example.com/path",
                "uri-reference": "/relative/path",
                "uri-template": "/users/{id}",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
            },
        )
        self.verzoek.full_clean()
