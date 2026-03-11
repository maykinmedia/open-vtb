import uuid

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.verzoeken.constants import VerzoekTypeVersionStatus
from openvtb.components.verzoeken.models import Verzoek, VerzoekType
from openvtb.components.verzoeken.tests.factories import (
    JSON_SCHEMA,
    VerzoekTypeFactory,
)
from openvtb.utils.api_testcase import APITestCase


class VerzoekValidatorsTests(APITestCase):
    maxDiff = None
    list_url = reverse("verzoeken:verzoek-list")

    def test_verzoektype_exists(self):
        self.assertFalse(Verzoek.objects.exists())

        # verzoekType does not exists
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(uuid.uuid4())}
            ),
            "aanvraagGegevens": {"diameter": 10},
            "versie": 1,
        }
        response = self.client.post(self.list_url, data)
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
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {"diameter": 10},
            "versie": 1,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Verzoek.objects.all().count(), 1)

    def test_verzoektype_versie_exists(self):
        verzoektype = VerzoekTypeFactory.create()

        # verzoekType versies does not exists
        self.assertFalse(verzoektype.versies.exists())
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {"diameter": 10},
            "versie": 1,
        }
        response = self.client.post(self.list_url, data)
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

        # POST new versie
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
        self.assertTrue(verzoektype.versies.exists())

        # re-CREATE Verzoek
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()
        self.assertEqual(verzoek.verzoek_type, verzoektype)
        self.assertEqual(verzoek.verzoek_type.last_versie.versie, 1)
        self.assertEqual(
            verzoek.verzoek_type.last_versie.aanvraag_gegevens_schema, JSON_SCHEMA
        )

        # re-CREATE Verzoek with non-existent versie
        data["versie"] = 2
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "versie"),
            {
                "name": "versie",
                "code": "unknown-schema",
                "reason": "Onbekend VerzoekType schema versie: geen schema beschikbaar.",
            },
        )

    def test_update_verzoek_with_new_versie(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {"diameter": 10},
            "versie": 1,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()

        # PUBLISH versie and POST NEW
        response = self.client.patch(
            reverse(
                "verzoeken:verzoektypeversion-detail",
                kwargs={
                    "verzoektype_uuid": str(verzoektype.uuid),
                    "verzoektype_versie": verzoektype.last_versie.versie,
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

        self.assertEqual(verzoek.verzoek_type.last_versie.versie, 2)
        self.assertEqual(
            verzoek.verzoek_type.last_versie.status, VerzoekTypeVersionStatus.DRAFT
        )

        # PUT same initial data for verzoek
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        # update data with the new versie
        data["versie"] = 2

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
                "versie": 2,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.aanvraag_gegevens["new_field"], "test")

    def test_update_verzoek_with_new_verzoektype(self):
        verzoektype_old = VerzoekTypeFactory.create(create_versie=True)
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail",
                kwargs={"uuid": str(verzoektype_old.uuid)},
            ),
            "aanvraagGegevens": {"diameter": 10},
            "versie": 1,
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()

        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        verzoektype_new = VerzoekTypeFactory.create(create_versie=True)
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
        verzoektype_old = VerzoekTypeFactory.create(create_versie=True)
        verzoektype_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype_old.uuid)}
        )

        with self.subTest("additional_properties not allowed"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10, "randomBool": False},
                "versie": 1,
            }
            response = self.client.post(self.list_url, data)

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
                "versie": 1,
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "aanvraagGegevens.diameter"),
                {
                    "name": "aanvraagGegevens.diameter",
                    "code": "invalid-json-schema",
                    "reason": "False is not of type 'integer'",
                },
            )

    def test_is_gerelateerd_aan_json_schema(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        verzoektype_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
        )

        with self.subTest("empty list"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "versie": 1,
                "isGerelateerdAan": [],
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data["is_gerelateerd_aan"], [])

        with self.subTest("object instead list"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "versie": 1,
                "isGerelateerdAan": {},
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isGerelateerdAan.nonFieldErrors"),
                {
                    "name": "isGerelateerdAan.nonFieldErrors",
                    "code": "not_a_list",
                    "reason": 'Verwachtte een lijst met items, maar kreeg type "dict".',
                },
            )

        with self.subTest("empty object"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "versie": 1,
                "isGerelateerdAan": [{}],
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isGerelateerdAan.0.urn"),
                {
                    "name": "isGerelateerdAan.0.urn",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
            )

        with self.subTest("invalid key"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "versie": 1,
                "isGerelateerdAan": [{}],
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isGerelateerdAan.0.urn"),
                {
                    "name": "isGerelateerdAan.0.urn",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
            )

        with self.subTest("invalid urn"):
            data = {
                "verzoekType": verzoektype_url,
                "aanvraagGegevens": {"diameter": 10},
                "versie": 1,
                "isGerelateerdAan": [{"urn": "1"}],
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "isGerelateerdAan.0.urn"),
                {
                    "name": "isGerelateerdAan.0.urn",
                    "code": "invalid_urn",
                    "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
                },
            )
