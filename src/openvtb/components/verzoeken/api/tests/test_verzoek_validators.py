import uuid

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.verzoeken.constants import VerzoekTypeVersionStatus
from openvtb.components.verzoeken.models import Verzoek, VerzoekType
from openvtb.components.verzoeken.tests.factories import (
    ADRES,
    JSON_SCHEMA,
    VerzoekFactory,
    VerzoekTypeFactory,
)
from openvtb.utils.api_testcase import APITestCase


class VerzoekValidatorsTests(APITestCase):
    maxDiff = None

    def test_verzoektype_exists(self):
        url = reverse("verzoeken:verzoek-list")
        self.assertFalse(Verzoek.objects.exists())

        # verzoekType does not exists
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(uuid.uuid4())}
            ),
            "aanvraagGegevens": {"diameter": 10},
            "version": 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "verzoekType"),
            {
                "name": "verzoekType",
                "code": "does_not_exist",
                "reason": "Ongeldige hyperlink - Object bestaat niet.",
            },
        )

        # verzoekType exists
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {"diameter": 10},
            "version": 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Verzoek.objects.all().count(), 1)

    def test_verzoektype_version_exists(self):
        url = reverse("verzoeken:verzoek-list")
        verzoektype = VerzoekTypeFactory.create()

        # verzoekType versions does not exists
        self.assertFalse(verzoektype.versions.exists())
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {"diameter": 10},
            "version": 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "verzoekType"),
            {
                "name": "verzoekType",
                "code": "unknown-schema",
                "reason": "Onbekend VerzoekType schema: geen schema beschikbaar.",
            },
        )

        # POST new version
        response = self.client.post(
            reverse(
                "verzoeken:verzoektypeversion-list",
                kwargs={"verzoektype_uuid": str(verzoektype.uuid)},
            ),
            {
                "aanvraagGegevensSchema": JSON_SCHEMA,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoektype = VerzoekType.objects.get()
        self.assertTrue(verzoektype.versions.exists())

        # re-CREATE Verzoek
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()
        self.assertEqual(verzoek.verzoek_type, verzoektype)
        self.assertEqual(verzoek.verzoek_type.last_version.version, 1)
        self.assertEqual(
            verzoek.verzoek_type.last_version.aanvraag_gegevens_schema, JSON_SCHEMA
        )

        # re-CREATE Verzoek with non-existent version
        data["version"] = 2
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "version"),
            {
                "name": "version",
                "code": "unknown-schema",
                "reason": "Onbekend VerzoekType schema versie: geen schema beschikbaar.",
            },
        )

    def test_update_verzoek_with_new_version(self):
        url = reverse("verzoeken:verzoek-list")
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 10,
            },
            "version": 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()

        # PUBLISH version and POST NEW
        response = self.client.patch(
            reverse(
                "verzoeken:verzoektypeversion-detail",
                kwargs={
                    "verzoektype_uuid": str(verzoektype.uuid),
                    "verzoektype_version": verzoektype.last_version.version,
                },
            ),
            {"status": VerzoekTypeVersionStatus.PUBLISHED},
        )
        new_json_schema = {
            "type": "object",
            "title": "Tree",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "required": ["new_field"],
            "properties": {"new_field": {"type": "string"}},
        }
        response = self.client.post(
            reverse(
                "verzoeken:verzoektypeversion-list",
                kwargs={
                    "verzoektype_uuid": str(verzoektype.uuid),
                },
            ),
            {"aanvraagGegevensSchema": new_json_schema},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(verzoek.verzoek_type.last_version.version, 2)
        self.assertEqual(
            verzoek.verzoek_type.last_version.status, VerzoekTypeVersionStatus.DRAFT
        )

        # PUT same initial data for verzoek
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        # update data with the new version
        data["version"] = 2

        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "aanvraagGegevens"),
            {
                "name": "aanvraagGegevens",
                "code": "invalid-json-schema",
                "reason": "'new_field' is a required property",
            },
        )

        # new data
        response = self.client.put(
            detail_url,
            {
                "verzoekType": reverse(
                    "verzoeken:verzoektype-detail",
                    kwargs={"uuid": str(verzoektype.uuid)},
                ),
                "aanvraagGegevens": {"new_field": "test"},
                "version": 2,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.aanvraag_gegevens["new_field"], "test")

    def test_update_verzoek_with_new_verzoektype(self):
        url = reverse("verzoeken:verzoek-list")

        verzoektype_old = VerzoekTypeFactory.create(create_version=True)
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail",
                kwargs={"uuid": str(verzoektype_old.uuid)},
            ),
            "aanvraagGegevens": {"diameter": 10},
            "version": 1,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()

        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        verzoektype_new = VerzoekTypeFactory.create(create_version=True)
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail",
                kwargs={"uuid": str(verzoektype_new.uuid)},
            ),
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "verzoekType"),
            {
                "name": "verzoekType",
                "code": "immutable-field",
                "reason": "Dit veld kan niet worden gewijzigd.",
            },
        )

    def test_invalid_json_schema(self):
        url = reverse("verzoeken:verzoek-list")

        verzoektype_old = VerzoekTypeFactory.create(create_version=True)
        verzoektype_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype_old.uuid)}
        )

        with self.subTest("additional_properties not allowed"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10, "randomBool": False},
                "version": 1,
            }
            response = self.client.post(url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "aanvraagGegevens"),
                {
                    "name": "aanvraagGegevens",
                    "code": "invalid-json-schema",
                    "reason": "Additional properties are not allowed ('randomBool' was unexpected)",
                },
            )

        with self.subTest("type not valid"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": False},
                "version": 1,
            }
            response = self.client.post(url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "aanvraagGegevens.diameter"),
                {
                    "name": "aanvraagGegevens.diameter",
                    "code": "invalid-json-schema",
                    "reason": "False is not of type 'integer'",
                },
            )

    def test_invalid_is_ingediend_door_json_schema(self):
        url = reverse("verzoeken:verzoek-list")

        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoektype_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
        )

        with self.subTest("multiple is_ingediend_door is not allowed"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {
                    "diameter": 10,
                },
                "version": 1,
                "isIngediendDoor": {
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
            response = self.client.post(url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isIngediendDoor"),
                {
                    "name": "isIngediendDoor",
                    "code": "invalid",
                    "reason": "It must have only one of the three permitted keys: one of `authentiekeVerwijzing`,"
                    " `nietAuthentiekePersoonsgegevens` or `nietAuthentiekeOrganisatiegegevens`.",
                },
            )

            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {
                    "diameter": 10,
                },
                "version": 1,
                "isIngediendDoor": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekePersoonsgegevens": None,
                    "nietAuthentiekeOrganisatiegegevens": None,
                },
            }
            response = self.client.post(url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isIngediendDoor"),
                {
                    "name": "isIngediendDoor",
                    "code": "invalid",
                    "reason": "It must have only one of the three permitted keys: one of `authentiekeVerwijzing`,"
                    " `nietAuthentiekePersoonsgegevens` or `nietAuthentiekeOrganisatiegegevens`.",
                },
            )
        with self.subTest("required field"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {
                    "diameter": 10,
                },
                "version": 1,
                "isIngediendDoor": {
                    "authentiekeVerwijzing": {"test": "1234"},
                },
            }
            response = self.client.post(url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(
                    response, "isIngediendDoor.authentiekeVerwijzing.urn"
                ),
                {
                    "name": "isIngediendDoor.authentiekeVerwijzing.urn",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
            )

    def test_create_address_json_schema(self):
        url = reverse("verzoeken:verzoek-list")

        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoektype_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
        )

        with self.subTest("null values"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "version": 1,
                "isIngediendDoor": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": None,
                        "postadres": None,
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(url, data)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isIngediendDoor"][
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
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "version": 1,
                "isIngediendDoor": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": {},
                        "postadres": {},
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isIngediendDoor"][
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
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "version": 1,
                "isIngediendDoor": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": {"woonplaats": "Amsterdam"},
                        "postadres": {"woonplaats": "Amsterdam"},
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            self.assertEqual(
                response.json()["isIngediendDoor"][
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
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "version": 1,
                "isIngediendDoor": {
                    "nietAuthentiekeOrganisatiegegevens": {
                        "statutaireNaam": "Acme BV",
                        "bezoekadres": ADRES,
                        "postadres": ADRES,
                        "emailadres": "info@acme.nl",
                        "telefoonnummer": "+31201234567",
                    },
                },
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["isIngediendDoor"][
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
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(
            create_details=True,
            verzoek_type=verzoektype,
            niet_authentieke_persoonsgegevens=True,
        )
        verzoek = Verzoek.objects.get()

        # initial assert
        self.assertEqual(
            verzoek.is_ingediend_door["nietAuthentiekePersoonsgegevens"]["postadres"],
            ADRES,
        )

        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        data = {
            "isIngediendDoor": {
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
        verzoek = Verzoek.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            verzoek.is_ingediend_door["nietAuthentiekePersoonsgegevens"]["postadres"],
            ADRES,
        )
        # postadres full updated
        self.assertEqual(
            verzoek.is_ingediend_door["nietAuthentiekePersoonsgegevens"]["postadres"],
            {"woonplaats": "Amsterdam"},
        )
