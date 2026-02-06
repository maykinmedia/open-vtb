import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from freezegun import freeze_time

from .factories import ADRES, ExterneTaakFactory


@freeze_time("2026-01-01")
class ValidateExterneTaakModelTestCase(TestCase):
    def test_valid_datum_herinnering(self):
        # set datum_herinnering
        einddatum_handelings_termijn = datetime.date.today()
        datum_herinnering = datetime.date.today() - datetime.timedelta(days=10)
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
            datum_herinnering=datum_herinnering,
        )
        taak.full_clean()
        self.assertEqual(taak.datum_herinnering, datum_herinnering)

        # empty datum_herinnering
        einddatum_handelings_termijn = datetime.date.today()
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
        )
        taak.full_clean()
        self.assertEqual(
            taak.datum_herinnering,
            (
                taak.einddatum_handelings_termijn
                - datetime.timedelta(settings.TAKEN_DEFAULT_REMINDER_IN_DAYS)
            ),
        )

        # TAKEN_DEFAULT_REMINDER_IN_DAYS unset
        with override_settings(TAKEN_DEFAULT_REMINDER_IN_DAYS=0):
            einddatum_handelings_termijn = datetime.date.today()
            taak = ExterneTaakFactory.create(
                betaaltaak=True,
                einddatum_handelings_termijn=einddatum_handelings_termijn,
            )
            taak.full_clean()
            self.assertEqual(taak.datum_herinnering, None)

    def test_invalid_dates(self):
        # set datum_herinnering > einddatum_handelings_termijn
        einddatum_handelings_termijn = datetime.date.today()
        datum_herinnering = einddatum_handelings_termijn + datetime.timedelta(days=10)
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
            datum_herinnering=datum_herinnering,
        )
        with self.assertRaises(ValidationError) as error:
            taak.full_clean()
        self.assertTrue("einddatum_handelings_termijn" in error.exception.message_dict)

        # set startdatum > einddatum_handelings_termijn
        einddatum_handelings_termijn = datetime.date.today()
        startdatum = einddatum_handelings_termijn + datetime.timedelta(days=10)
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
            startdatum=startdatum,
        )
        with self.assertRaises(ValidationError) as error:
            taak.full_clean()
        self.assertTrue("einddatum_handelings_termijn" in error.exception.message_dict)


class ValidateExterneTaakisIngediendDoorJsonSchemaTestCase(TestCase):
    def test_valid_schemas(self):
        taak = ExterneTaakFactory.create(betaaltaak=True)

        # authentiekeVerwijzing
        taak.is_toegewezen_aan = {
            "authentiekeVerwijzing": {
                "urn": "urn:nld:brp:bsn:111222333",
            }
        }
        taak.save()
        taak.full_clean()

        # authentiekeVerwijzing
        taak.is_toegewezen_aan = {
            "nietAuthentiekePersoonsgegevens": {
                "voornaam": "Pietje",
                "achternaam": "Puk",
                "geboortedatum": "1982-01-01",
                "emailadres": "test@admin.com",
                "telefoonnummer": "",
                "postadres": ADRES,
                "verblijfsadres": ADRES,
            }
        }
        taak.save()
        taak.full_clean()

        # authentiekeVerwijzing
        taak.is_toegewezen_aan = {
            "nietAuthentiekeOrganisatiegegevens": {
                "statutaireNaam": "ACME",
                "bezoekadres": ADRES,
                "postadres": ADRES,
                "emailadres": "test@admin.com",
                "telefoonnummer": "",
            }
        }
        taak.save()
        taak.full_clean()

    def test_invalid_authentieke_verwijzing_schema(self):
        taak = ExterneTaakFactory.create(betaaltaak=True)

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {"authentiekeVerwijzing": {}}
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.authentiekeVerwijzing': [\"'urn' is a required property\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "authentiekeVerwijzing": {
                    "test": 1,
                }
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan': [\"{'authentiekeVerwijzing': {'test': 1}} is not valid under any of the given schemas\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "authentiekeVerwijzing": {
                    "urn": "test",
                }
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.authentiekeVerwijzing.urn': [\"'test' does not match '^urn:.*$'\"]}"
                ]
            },
        )

    def test_invalid_niet_authentieke_persoonsgegevens_schema(self):
        taak = ExterneTaakFactory.create(betaaltaak=True)

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {"nietAuthentiekePersoonsgegevens": {}}
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan': [\"{'nietAuthentiekePersoonsgegevens': {}} is not valid under any of the given schemas\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekePersoonsgegevens": {
                    "test": 1,
                }
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan': [\"{'nietAuthentiekePersoonsgegevens': {'test': 1}} is not valid under any of the given schemas\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": 1,
                    "achternaam": "Puk",
                    "geboortedatum": "1982-01-01",
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                    "postadres": ADRES,
                    "verblijfsadres": ADRES,
                },
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.nietAuthentiekePersoonsgegevens.voornaam': [\"1 is not of type 'string'\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": "Jan",
                    "achternaam": "Puk",
                    "geboortedatum": "1982-01-01",
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                    "postadres": {"key": "value"},
                    "verblijfsadres": {"key": "value"},
                },
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.nietAuthentiekePersoonsgegevens.postadres': [\"Additional properties are not allowed ('key' was unexpected)\"]}"
                ]
            },
        )
        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": 1,
                    "achternaam": "Puk",
                    "geboortedatum": "1982-01-01",
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                    "postadres": {"woonplaats": 1},  # wrong type
                    "verblijfsadres": ADRES,
                },
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.nietAuthentiekePersoonsgegevens.postadres.woonplaats': [\"1 is not of type 'string'\"]}"
                ]
            },
        )

    def test_invalid_niet_authentieke_organisatiegegevens_schema(self):
        taak = ExterneTaakFactory.create(betaaltaak=True)

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {"nietAuthentiekeOrganisatiegegevens": {}}
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan': [\"{'nietAuthentiekeOrganisatiegegevens': {}} is not valid under any of the given schemas\"]}"
                ]
            },
        )
        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekeOrganisatiegegevens": {
                    "test": 1,
                }
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan': [\"{'nietAuthentiekeOrganisatiegegevens': {'test': 1}} is not valid under any of the given schemas\"]}"
                ]
            },
        )
        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": 1,
                    "bezoekadres": ADRES,
                    "postadres": ADRES,
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                },
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.nietAuthentiekeOrganisatiegegevens.statutaireNaam': [\"1 is not of type 'string'\"]}"
                ]
            },
        )
        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": "test",
                    "bezoekadres": {"key": "value"},
                    "postadres": {"key": "value"},
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                },
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.nietAuthentiekeOrganisatiegegevens.bezoekadres': [\"Additional properties are not allowed ('key' was unexpected)\"]}"
                ]
            },
        )

        with self.assertRaises(ValidationError) as error:
            taak.is_toegewezen_aan = {
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": "test",
                    "bezoekadres": {"woonplaats": 1},
                    "postadres": ADRES,
                    "emailadres": "test@admin.com",
                    "telefoonnummer": "",
                },
            }
            taak.save()
            taak.full_clean()
        self.assertEqual(
            error.exception.message_dict,
            {
                "is_toegewezen_aan": [
                    "{'is_toegewezen_aan.nietAuthentiekeOrganisatiegegevens.bezoekadres.woonplaats': [\"1 is not of type 'string'\"]}"
                ]
            },
        )
