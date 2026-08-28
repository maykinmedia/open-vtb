import datetime
import uuid

from django.utils import timezone

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.berichten.tests.factories import (
    BerichtFactory,
    BerichtTypeFactory,
)
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-02-02 13:52:00")
class BerichtFilterTest(APITestCase):
    list_url = reverse("berichten:bericht-list")

    def setUp(self):
        super().setUp()
        self.now = timezone.now()

        self.urn_zaak = "urn:nld:gemeenteutrecht:zaak:zaaknummer:000350165"
        self.urn_product = (
            "urn:nld:gemeenteutrecht:product:uuid:717815f6-1939-4fd2-93f0-83d25bad154e"
        )

        self.bericht_type_a = BerichtTypeFactory.create()
        self.bericht_type_b = BerichtTypeFactory.create()

        self.bericht_a = BerichtFactory.create(
            ontvanger="urn:maykin:123",
            publicatiedatum=self.now - datetime.timedelta(days=5),
            geopend_op=self.now - datetime.timedelta(days=4),
            is_gerelateerd_aan=[{"urn": self.urn_zaak}],
            bericht_type=self.bericht_type_a,
        )
        self.bericht_b = BerichtFactory.create(
            ontvanger="urn:maykin:456",
            publicatiedatum=self.now - datetime.timedelta(days=1),
            geopend_op=None,
            is_gerelateerd_aan=[{"urn": self.urn_product}],
            bericht_type=self.bericht_type_a,
        )
        self.bericht_c = BerichtFactory.create(
            ontvanger="urn:maykin:789",
            publicatiedatum=self.now + datetime.timedelta(days=5),
            geopend_op=None,
            is_gerelateerd_aan=[{"urn": self.urn_zaak}, {"urn": self.urn_product}],
            bericht_type=self.bericht_type_b,
        )

    def test_filter_bericht_type_uuid(self):
        response = self.client.get(
            self.list_url, {"berichtType__uuid": self.bericht_type_a.uuid}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(
            data["results"][0]["berichtType"],
            f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(self.bericht_type_a.uuid)})}",
        )

        response = self.client.get(
            self.list_url, {"berichtType__uuid": self.bericht_type_b.uuid}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["berichtType"],
            f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(self.bericht_type_b.uuid)})}",
        )

        # random uuid
        response = self.client.get(self.list_url, {"berichtType__uuid": uuid.uuid4()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 0)

        # wrong uuid
        response = self.client.get(self.list_url, {"berichtType__uuid": "test"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "berichtType__uuid"),
            {
                "name": "berichtType__uuid",
                "code": "invalid",
                "reason": "Voer een geldige UUID in.",
            },
        )

    def test_filter_bericht_type_urn(self):
        response = self.client.get(
            self.list_url,
            {
                "berichtType__urn": f"urn:maykin:berichten:berichttype:{str(self.bericht_type_a.uuid)}"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(
            data["results"][0]["berichtType"],
            f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(self.bericht_type_a.uuid)})}",
        )

        response = self.client.get(
            self.list_url,
            {
                "berichtType__urn": f"urn:maykin:berichten:berichttype:{str(self.bericht_type_b.uuid)}"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["berichtType"],
            f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(self.bericht_type_b.uuid)})}",
        )

        # random uuid
        response = self.client.get(
            self.list_url,
            {"berichtType__urn": "urn:maykin:berichten:berichttype:1234"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "berichtType__urn"),
            {
                "name": "berichtType__urn",
                "code": "invalid",
                "reason": "Invalid or unknown URN.",
            },
        )

        # wrong uuid
        response = self.client.get(
            self.list_url,
            {"berichtType__urn": "test"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "berichtType__urn"),
            {
                "name": "berichtType__urn",
                "code": "invalid",
                "reason": "Invalid or unknown URN.",
            },
        )

    def test_filter_ontvanger(self):
        response = self.client.get(self.list_url, {"ontvanger": "urn:maykin:123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.bericht_a.uuid))

        # random urn
        response = self.client.get(self.list_url, {"ontvanger": "urn:maykin:test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 0)

    def test_filter_publicatiedatum(self):
        with self.subTest("exact"):
            response = self.client.get(
                self.list_url,
                {"publicatiedatum": self.bericht_a.publicatiedatum.isoformat()},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.bericht_a.uuid))

        with self.subTest("gt"):
            response = self.client.get(
                self.list_url,
                {"publicatiedatum__gt": self.now.isoformat()},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.bericht_c.uuid))

        with self.subTest("gte"):
            response = self.client.get(
                self.list_url,
                {"publicatiedatum__gte": self.bericht_b.publicatiedatum.isoformat()},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            uuids = {result["uuid"] for result in data["results"]}
            self.assertEqual(
                uuids, {str(self.bericht_b.uuid), str(self.bericht_c.uuid)}
            )

        with self.subTest("lt"):
            response = self.client.get(
                self.list_url,
                {"publicatiedatum__lt": self.now.isoformat()},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            uuids = {result["uuid"] for result in data["results"]}
            self.assertEqual(
                uuids, {str(self.bericht_a.uuid), str(self.bericht_b.uuid)}
            )

        with self.subTest("lte"):
            response = self.client.get(
                self.list_url,
                {"publicatiedatum__lte": self.bericht_b.publicatiedatum.isoformat()},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            uuids = {result["uuid"] for result in data["results"]}
            self.assertEqual(
                uuids, {str(self.bericht_a.uuid), str(self.bericht_b.uuid)}
            )

    def test_filter_geopend_op_isnull(self):
        with self.subTest("true"):
            response = self.client.get(self.list_url, {"geopendOp__isnull": "true"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            uuids = {result["uuid"] for result in data["results"]}
            self.assertEqual(
                uuids, {str(self.bericht_b.uuid), str(self.bericht_c.uuid)}
            )

        with self.subTest("false"):
            response = self.client.get(self.list_url, {"geopendOp__isnull": "false"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.bericht_a.uuid))

        with self.subTest("invalid"):
            response = self.client.get(self.list_url, {"geopendOp__isnull": "test"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            # return all values
            self.assertEqual(data["count"], 3)

    def test_filter_is_gerelateerd_aan(self):
        with self.subTest("zaak"):
            response = self.client.get(
                self.list_url, {"isGerelateerdAan": self.urn_zaak}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            uuids = {result["uuid"] for result in data["results"]}
            self.assertEqual(
                uuids, {str(self.bericht_a.uuid), str(self.bericht_c.uuid)}
            )

        with self.subTest("product"):
            response = self.client.get(
                self.list_url, {"isGerelateerdAan": self.urn_product}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            uuids = {result["uuid"] for result in data["results"]}
            self.assertEqual(
                uuids, {str(self.bericht_b.uuid), str(self.bericht_c.uuid)}
            )
        with self.subTest("no match"):
            response = self.client.get(
                self.list_url,
                {
                    "isGerelateerdAan": "urn:nld:gemeenteutrecht:zaak:zaaknummer:999999999"
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 0)
