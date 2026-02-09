import datetime

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import ADRES, ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


class ExterneTaakValidationTests(APITestCase):
    list_url = reverse("taken:externetaak-list")
    details = {
        "bedrag": "11",
        "transactieomschrijving": "test",
        "doelrekening": {
            "naam": "test",
            "code": "123-ABC",
            "iban": "NL12BANK34567890",
        },
    }

    def test_invalid_create_type_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "test",
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "startdatum": datetime.date(2026, 1, 10),  # end < start
            "einddatumHandelingsTermijn": datetime.date(2025, 1, 10),
            "details": self.details,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "einddatumHandelingsTermijn"),
            {
                "name": "einddatumHandelingsTermijn",
                "code": "date-mismatch",
                "reason": "startdatum should be before einddatum_handelings_termijn.",
            },
        )
        self.assertFalse(ExterneTaak.objects.exists())

    def test_invalid_create_urn_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "wordtBehandeldDoor": "test:maykin:medewerker:brp:nnp:bsn:1234567892",  # doesn't start with urn
            "hoortBij": "urn:maykinmaykinmaykinmaykinmaykinmaykinmaykinmaykinmaykin:1",  # long NID
            "details": self.details,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(
            get_validation_errors(response, "wordtBehandeldDoor"),
            {
                "name": "wordtBehandeldDoor",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "hoortBij"),
            {
                "name": "hoortBij",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertFalse(ExterneTaak.objects.exists())

    def test_invalid_is_toegewezen_aan_json_schema(self):
        with self.subTest("multiple is_toegewezen_aan is not allowed"):
            # invalid isToegewezenAan schema
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.BETAALTAAK.value,
                "details": self.details,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": {"urn": "urn:example:12345"},
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": {"key": "value"},
                        "postadres": {"key": "value"},
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isToegewezenAan"),
                {
                    "name": "isToegewezenAan",
                    "code": "invalid",
                    "reason": "It must have only one of the three permitted keys: one of `authentiekeVerwijzing`,"
                    " `nietAuthentiekePersoonsgegevens` or `nietAuthentiekeOrganisatiegegevens`.",
                },
            )

            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.BETAALTAAK.value,
                "details": self.details,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekePersoonsgegevens": None,
                    "nietAuthentiekeOrganisatiegegevens": None,
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isToegewezenAan"),
                {
                    "name": "isToegewezenAan",
                    "code": "invalid",
                    "reason": "It must have only one of the three permitted keys: one of `authentiekeVerwijzing`,"
                    " `nietAuthentiekePersoonsgegevens` or `nietAuthentiekeOrganisatiegegevens`.",
                },
            )
        with self.subTest("required field"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.BETAALTAAK.value,
                "details": self.details,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": {"test": "1234"},
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(
                    response, "isToegewezenAan.authentiekeVerwijzing.urn"
                ),
                {
                    "name": "isToegewezenAan.authentiekeVerwijzing.urn",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
            )

    def test_create_address_json_schema(self):
        with self.subTest("null values"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.BETAALTAAK.value,
                "details": self.details,
                "isToegewezenAan": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": None,
                        "postadres": None,
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isToegewezenAan"][
                    "nietAuthentiekeOrganisatiegegevens"
                ],
                {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": None,
                    "postadres": None,
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                },
            )

        with self.subTest("empty values"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.BETAALTAAK.value,
                "details": self.details,
                "isToegewezenAan": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": {},
                        "postadres": {},
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isToegewezenAan"][
                    "nietAuthentiekeOrganisatiegegevens"
                ],
                {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": {},
                    "postadres": {},
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                },
            )

        with self.subTest("set one field"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.BETAALTAAK.value,
                "details": self.details,
                "isToegewezenAan": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": {"woonplaats": "Amsterdam"},
                        "postadres": {"woonplaats": "Amsterdam"},
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            self.assertEqual(
                response.json()["isToegewezenAan"][
                    "nietAuthentiekeOrganisatiegegevens"
                ],
                {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": {"woonplaats": "Amsterdam"},
                    "postadres": {"woonplaats": "Amsterdam"},
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                },
            )
        with self.subTest("set all fields"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.BETAALTAAK.value,
                "details": self.details,
                "isToegewezenAan": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": ADRES,
                        "postadres": ADRES,
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isToegewezenAan"][
                    "nietAuthentiekeOrganisatiegegevens"
                ],
                {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": ADRES,
                    "postadres": ADRES,
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                },
            )

    def test_update_address_json_schema(self):
        betaaltaak = ExterneTaakFactory.create(
            betaaltaak=True, niet_authentieke_persoonsgegevens=True
        )

        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )

        # initial assert
        self.assertEqual(
            betaaltaak.is_toegewezen_aan["nietAuthentiekePersoonsgegevens"][
                "postadres"
            ],
            ADRES,
        )

        data = {
            "isToegewezenAan": {
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": "Jan",
                    "achternaam": "Jansen",
                    "geboortedatum": "1980-05-15",
                    "emailadres": "jan.jansen@example.com",
                    "telefoonnummer": "+31612345678",
                    "postadres": {"woonplaats": "Amsterdam"},
                    "verblijfsadres": None,
                }
            },
        }
        response = self.client.patch(detail_url, data)
        taak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            taak.is_toegewezen_aan["nietAuthentiekePersoonsgegevens"]["postadres"],
            ADRES,
        )
        # postadres full updated
        self.assertEqual(
            taak.is_toegewezen_aan["nietAuthentiekePersoonsgegevens"]["postadres"],
            {"woonplaats": "Amsterdam"},
        )

    def test_create_address_validate_buitenland(self):
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "details": self.details,
            "isToegewezenAan": {
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": None,
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                },
            },
        }
        with self.subTest("local_fields `yes` and buitenland `no`"):
            data["isToegewezenAan"]["nietAuthentiekeOrganisatiegegevens"][
                "postadres"
            ] = {
                "woonplaats": "Amsterdam",
                "postcode": "1000 AB",
                "huisnummer": "12",
                "huisletter": "A",
                "huisnummertoevoeging": "bis",
                # "buitenland": {},
            }

            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isToegewezenAan"][
                    "nietAuthentiekeOrganisatiegegevens"
                ]["postadres"],
                {
                    "woonplaats": "Amsterdam",
                    "postcode": "1000 AB",
                    "huisnummer": "12",
                    "huisletter": "A",
                    "huisnummertoevoeging": "bis",
                    # "buitenland": {},
                },
            )

        with self.subTest("local_fields `yes` and buitenland `yes`"):
            data["isToegewezenAan"]["nietAuthentiekeOrganisatiegegevens"][
                "postadres"
            ] = {
                "woonplaats": "Amsterdam",
                "postcode": "1000 AB",
                "huisnummer": "12",
                "huisletter": "A",
                "huisnummertoevoeging": "bis",
                "buitenland": {},
            }

            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(
                    response,
                    "isToegewezenAan.nietAuthentiekeOrganisatiegegevens.postadres.buitenland",
                ),
                {
                    "name": "isToegewezenAan.nietAuthentiekeOrganisatiegegevens.postadres.buitenland",
                    "code": "invalid",
                    "reason": "This field can only be filled in if the local address fields are not specified.",
                },
            )

            data["isToegewezenAan"]["nietAuthentiekeOrganisatiegegevens"][
                "postadres"
            ] = {
                "woonplaats": "Amsterdam",
                "postcode": "1000 AB",
                "huisnummer": "12",
                "huisletter": "A",
                "huisnummertoevoeging": "bis",
                "buitenland": {
                    "landcode": "AB",
                    "landnaam": "test",
                },
            }

            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(
                get_validation_errors(
                    response,
                    "isToegewezenAan.nietAuthentiekeOrganisatiegegevens.postadres.buitenland",
                ),
                {
                    "name": "isToegewezenAan.nietAuthentiekeOrganisatiegegevens.postadres.buitenland",
                    "code": "invalid",
                    "reason": "This field can only be filled in if the local address fields are not specified.",
                },
            )

            data["isToegewezenAan"]["nietAuthentiekeOrganisatiegegevens"][
                "postadres"
            ] = {
                # "woonplaats": "Amsterdam",
                # "postcode": "1000 AB",
                # "huisnummer": "12",
                # "huisletter": "A",
                "huisnummertoevoeging": "bis",
                "buitenland": {
                    "landcode": "AB",
                    "landnaam": "test",
                },
            }

            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(
                get_validation_errors(
                    response,
                    "isToegewezenAan.nietAuthentiekeOrganisatiegegevens.postadres.buitenland",
                ),
                {
                    "name": "isToegewezenAan.nietAuthentiekeOrganisatiegegevens.postadres.buitenland",
                    "code": "invalid",
                    "reason": "This field can only be filled in if the local address fields are not specified.",
                },
            )

        with self.subTest("local_fields `no` and buitenland `yes`"):
            data["isToegewezenAan"]["nietAuthentiekeOrganisatiegegevens"][
                "postadres"
            ] = {
                "buitenland": {
                    "landcode": "AB",
                    "landnaam": "test",
                },
            }

            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isToegewezenAan"][
                    "nietAuthentiekeOrganisatiegegevens"
                ]["postadres"],
                {
                    "buitenland": {
                        "landcode": "AB",
                        "landnaam": "test",
                    },
                },
            )
