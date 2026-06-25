from datetime import date

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.constants import HandelingsPerspectiefEnum
from openvtb.components.taken.constants import StatusTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


class ExterneTaakFilterTest(APITestCase):
    list_url = reverse("taken:externetaak-list")

    def setUp(self):
        super().setUp()
        self.taak_a = ExterneTaakFactory.create(
            titel="externetaak A",
            status=StatusTaak.OPEN,
            handelings_perspectief=HandelingsPerspectiefEnum.BETALEN,
            is_toegewezen_aan="urn:maykin:123",
            startdatum=date(2026, 1, 10),
            einddatum_handelings_termijn=date(2026, 3, 31),
            datum_herinnering=date(2026, 2, 15),
        )
        self.taak_b = ExterneTaakFactory.create(
            titel="externetaak B",
            status=StatusTaak.UITGEVOERD,
            handelings_perspectief=HandelingsPerspectiefEnum.INCASSO,
            is_toegewezen_aan="urn:maykin:456",
            startdatum=date(2026, 4, 1),
            einddatum_handelings_termijn=date(2026, 6, 30),
            datum_herinnering=date(2026, 5, 1),
        )
        self.taak_c = ExterneTaakFactory.create(
            titel="externetaak C",
            status=StatusTaak.VERWERKT,
            handelings_perspectief=HandelingsPerspectiefEnum.BETALEN,
            is_toegewezen_aan="urn:maykin:789",
            startdatum=date(2026, 7, 1),
            einddatum_handelings_termijn=date(2026, 9, 30),
            datum_herinnering=date(2026, 8, 1),
        )

    def test_filter_uuid(self):
        response = self.client.get(self.list_url, {"uuid": str(self.taak_a.uuid)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

    def test_filter_titel(self):
        response = self.client.get(self.list_url, {"titel": "externetaak A"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

    def test_filter_status(self):
        with self.subTest("OPEN"):
            response = self.client.get(self.list_url, {"status": StatusTaak.OPEN})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("UITGEVOERD"):
            response = self.client.get(self.list_url, {"status": StatusTaak.UITGEVOERD})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_b.uuid))

        with self.subTest("VERWERKT"):
            response = self.client.get(self.list_url, {"status": StatusTaak.VERWERKT})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_c.uuid))

            # new status
            ExterneTaakFactory.create(status=StatusTaak.VERWERKT)
            response = self.client.get(self.list_url, {"status": StatusTaak.VERWERKT})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)

        with self.subTest("invalid choice"):
            response = self.client.get(self.list_url, {"status": "test"})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "status"),
                {
                    "name": "status",
                    "code": "invalid_choice",
                    "reason": "Selecteer een geldige keuze. test is geen beschikbare keuze.",
                },
            )

    def test_filter_handelings_perspectief(self):
        with self.subTest("BETALEN"):
            response = self.client.get(
                self.list_url,
                {"handelingsPerspectief": HandelingsPerspectiefEnum.BETALEN},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_a.uuid), str(self.taak_c.uuid)}
            )

        with self.subTest("invalid choice"):
            response = self.client.get(self.list_url, {"handelingsPerspectief": "test"})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "handelingsPerspectief"),
                {
                    "name": "handelingsPerspectief",
                    "code": "invalid_choice",
                    "reason": "Selecteer een geldige keuze. test is geen beschikbare keuze.",
                },
            )

    def test_filter_is_toegewezen_aan(self):
        with self.subTest("exact"):
            response = self.client.get(
                self.list_url, {"isToegewezenAan": "urn:maykin:123"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("not found"):
            response = self.client.get(self.list_url, {"isToegewezenAan": "test"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 0)

    def test_filter_startdatum(self):
        with self.subTest("exact"):
            response = self.client.get(self.list_url, {"startdatum": "2026-01-10"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("gt"):
            response = self.client.get(self.list_url, {"startdatum__gt": "2026-04-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_c.uuid))

        with self.subTest("gte"):
            response = self.client.get(self.list_url, {"startdatum__gte": "2026-04-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_b.uuid), str(self.taak_c.uuid)}
            )

        with self.subTest("lt"):
            response = self.client.get(self.list_url, {"startdatum__lt": "2026-04-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("lte"):
            response = self.client.get(self.list_url, {"startdatum__lte": "2026-04-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_a.uuid), str(self.taak_b.uuid)}
            )

        with self.subTest("range gte + lte"):
            response = self.client.get(
                self.list_url,
                {
                    "startdatum__gte": "2026-01-10",
                    "startdatum__lte": "2026-04-01",
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_a.uuid), str(self.taak_b.uuid)}
            )

    def test_filter_einddatum_handelings_termijn(self):
        with self.subTest("exact"):
            response = self.client.get(
                self.list_url, {"einddatumHandelingsTermijn": "2026-03-31"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("gt"):
            response = self.client.get(
                self.list_url, {"einddatumHandelingsTermijn__gt": "2026-06-30"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_c.uuid))

        with self.subTest("gte"):
            response = self.client.get(
                self.list_url, {"einddatumHandelingsTermijn__gte": "2026-06-30"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_b.uuid), str(self.taak_c.uuid)}
            )

        with self.subTest("lt"):
            response = self.client.get(
                self.list_url, {"einddatumHandelingsTermijn__lt": "2026-06-30"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("lte"):
            response = self.client.get(
                self.list_url, {"einddatumHandelingsTermijn__lte": "2026-06-30"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_a.uuid), str(self.taak_b.uuid)}
            )

        with self.subTest("range gte + lte"):
            response = self.client.get(
                self.list_url,
                {
                    "einddatumHandelingsTermijn__gte": "2026-03-31",
                    "einddatumHandelingsTermijn__lte": "2026-06-30",
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_a.uuid), str(self.taak_b.uuid)}
            )

    def test_filter_datum_herinnering(self):
        with self.subTest("exact"):
            response = self.client.get(
                self.list_url, {"datumHerinnering": "2026-02-15"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("gt"):
            response = self.client.get(
                self.list_url, {"datumHerinnering__gt": "2026-05-01"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_c.uuid))

        with self.subTest("gte"):
            response = self.client.get(
                self.list_url, {"datumHerinnering__gte": "2026-05-01"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_b.uuid), str(self.taak_c.uuid)}
            )

        with self.subTest("lt"):
            response = self.client.get(
                self.list_url, {"datumHerinnering__lt": "2026-05-01"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["results"][0]["uuid"], str(self.taak_a.uuid))

        with self.subTest("lte"):
            response = self.client.get(
                self.list_url, {"datumHerinnering__lte": "2026-05-01"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_a.uuid), str(self.taak_b.uuid)}
            )

        with self.subTest("range gte + lte"):
            response = self.client.get(
                self.list_url,
                {
                    "datumHerinnering__gte": "2026-02-15",
                    "datumHerinnering__lte": "2026-05-01",
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["count"], 2)
            result_uuids = {r["uuid"] for r in data["results"]}
            self.assertEqual(
                result_uuids, {str(self.taak_a.uuid), str(self.taak_b.uuid)}
            )
