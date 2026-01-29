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
        with self.assertRaises(ValidationError) as error:
            self.verzoek = VerzoekFactory.create(aanvraag_gegevens={"diameter": 1})
            self.verzoek.full_clean()

        self.assertFalse(self.verzoek.verzoek_type.versions.exists())
        self.assertEqual(
            error.exception.message_dict,
            {
                "version": [
                    "Onbekend VerzoekType schema versie: geen schema beschikbaar."
                ]
            },
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


class ValidateVerzoekisIngediendDoorJsonSchemaTestCase(TestCase):
    def test_valid_authentieke_verwijzing_schema(self):
        verzoek_type = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(verzoek_type=verzoek_type)

        # authentiekeVerwijzing
        verzoek.is_ingediend_door = {
            "authentiekeVerwijzing": {
                "urn": "urn:nld:brp:bsn:111222333",
            }
        }
        verzoek.save()
        verzoek.full_clean()

        # authentiekeVerwijzing
        verzoek.is_ingediend_door = {
            "nietAuthentiekePersoonsgegevens": {
                "voornaam": "Pietje",
                "achternaam": "Puk",
                "geboortedatum": "1982-01-01",
                "emailadres": "test@admin.com",
                "telefoonnummer": "",
                "postadres": "",
                "verblijfsadres": "",
            }
        }
        verzoek.save()
        verzoek.full_clean()

        # authentiekeVerwijzing
        verzoek.is_ingediend_door = {
            "nietAuthentiekeOrganisatiegegevens": {
                "statutaireNaam": "ACME",
                "bezoekadres": "",
                "postadres": "",
                "emailadres": "test@admin.com",
                "telefoonnummer": "",
            }
        }
        verzoek.save()
        verzoek.full_clean()

    def test_invalid_authentieke_verwijzing_schema(self):
        verzoek_type = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(verzoek_type=verzoek_type)

        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {"authentiekeVerwijzing": {}}
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door.authentiekeVerwijzing': [\"'urn' is a required property\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {
                "authentiekeVerwijzing": {
                    "test": 1,
                }
            }
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door': [\"{'authentiekeVerwijzing': {'test': 1}} is not valid under any of the given schemas\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {
                "authentiekeVerwijzing": {
                    "urn": "test",
                }
            }
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door.authentiekeVerwijzing.urn': [\"'test' does not match '^urn:.*$'\"]}"
                ]
            },
        )

    def test_invalid_niet_authentieke_persoonsgegevens_schema(self):
        verzoek_type = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(verzoek_type=verzoek_type)

        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {"nietAuthentiekePersoonsgegevens": {}}
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door': [\"{'nietAuthentiekePersoonsgegevens': {}} is not valid under any of the given schemas\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {
                "nietAuthentiekePersoonsgegevens": {
                    "test": 1,
                }
            }
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door': [\"{'nietAuthentiekePersoonsgegevens': {'test': 1}} is not valid under any of the given schemas\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": 1,
                    "achternaam": "Puk",
                    "geboortedatum": "1982-01-01",
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                    "postadres": "",
                    "verblijfsadres": "",
                },
            }
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door.nietAuthentiekePersoonsgegevens.voornaam': [\"1 is not of type 'string'\"]}"
                ]
            },
        )

    def test_invalid_niet_authentieke_organisatiegegevens_schema(self):
        verzoek_type = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(verzoek_type=verzoek_type)

        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {"nietAuthentiekeOrganisatiegegevens": {}}
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door': [\"{'nietAuthentiekeOrganisatiegegevens': {}} is not valid under any of the given schemas\"]}"
                ]
            },
        )
        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {
                "nietAuthentiekeOrganisatiegegevens": {
                    "test": 1,
                }
            }
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door': [\"{'nietAuthentiekeOrganisatiegegevens': {'test': 1}} is not valid under any of the given schemas\"]}"
                ]
            },
        )
        with self.assertRaises(ValidationError) as error:
            verzoek.is_ingediend_door = {
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": 1,
                    "bezoekadres": "",
                    "postadres": "",
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                },
            }
            verzoek.save()
            verzoek.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_ingediend_door": [
                    "{'is_ingediend_door.nietAuthentiekeOrganisatiegegevens.statutaireNaam': [\"1 is not of type 'string'\"]}"
                ]
            },
        )
