import uuid

from rest_framework import status
from vng_api_common.tests import reverse

from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


class ExterneTaakTests(APITestCase):
    list_url = reverse("taken:externetaak-list")

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        ExterneTaakFactory.create()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        externetaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "uuid": str(externetaak.uuid),
                        "titel": externetaak.titel,
                        "status": externetaak.status,
                        "startdatum": externetaak.startdatum,
                        "handelingsPerspectief": externetaak.handelings_perspectief,
                        "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "datumHerinnering": externetaak.datum_herinnering,
                        "toelichting": externetaak.toelichting,
                        "taakSoort": externetaak.taak_soort,
                    }
                ],
            },
        )

        # list all sorts of tasks
        ExterneTaakFactory.create(betaaltaak=True)
        ExterneTaakFactory.create(gegevensuitvraagtaak=True)
        ExterneTaakFactory.create(formuliertaak=True)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 4)
        self.assertEqual(ExterneTaak.objects.all().count(), 4)

    def test_list_pagination_pagesize_param(self):
        ExterneTaakFactory.create_batch(10)
        response = self.client.get(self.list_url, {"pageSize": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(response.json()["count"], 10)
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertEqual(
            data["next"], f"http://testserver{self.list_url}?page=2&pageSize=5"
        )

    def test_detail(self):
        externetaak = ExterneTaakFactory.create()
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "uuid": str(externetaak.uuid),
                "titel": externetaak.titel,
                "status": externetaak.status,
                "startdatum": None,
                "handelingsPerspectief": externetaak.handelings_perspectief,
                "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": None,
                "toelichting": "",
                "taakSoort": "",
            },
        )

    def test_detail_not_found(self):
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(uuid.uuid4())}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_not_allowed(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_partial_not_allowed(self):
        externetaak = ExterneTaakFactory.create()
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_not_allowed(self):
        externetaak = ExterneTaakFactory.create()
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )
        response = self.client.put(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_destroynot_allowed(self):
        externetaak = ExterneTaakFactory.create()
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
