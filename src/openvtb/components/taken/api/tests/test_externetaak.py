import uuid

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak, StatusTaak
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

    def test_valid_create(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief",
            "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        externetaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "uuid": str(externetaak.uuid),
                "titel": "titel",
                "status": StatusTaak.OPEN.value,  # default value
                "startdatum": None,
                "handelingsPerspectief": "handelingsPerspectief",
                "einddatumHandelingsTermijn": "2025-01-01T12:00:00Z",
                "datumHerinnering": None,
                "toelichting": "",
                "taakSoort": "",
            },
        )

        # create ExterneTaak without data
        data = {
            "titel": "titel2",
            "handelingsPerspectief": "handelingsPerspectief2",
            "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
            "taakSoort": SoortTaak.BETAALTAAK.value,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 2)

        externetaak = ExterneTaak.objects.get(taak_soort=SoortTaak.BETAALTAAK.value)
        self.assertEqual(
            response.json(),
            {
                "uuid": str(externetaak.uuid),
                "titel": "titel2",
                "status": StatusTaak.OPEN.value,  # default value
                "startdatum": None,
                "handelingsPerspectief": "handelingsPerspectief2",
                "einddatumHandelingsTermijn": "2025-01-01T12:00:00Z",
                "datumHerinnering": None,
                "toelichting": "",
                "taakSoort": SoortTaak.BETAALTAAK.value,
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 3)
        self.assertEqual(
            get_validation_errors(response, "titel"),
            {
                "name": "titel",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "handelingsPerspectief"),
            {
                "name": "handelingsPerspectief",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "einddatumHandelingsTermijn"),
            {
                "name": "einddatumHandelingsTermijn",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

    def test_invalid_create_type_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        with self.subTest("invalid einddatumHandelingsTermijn value"):
            data = {
                "titel": "TestTitle",
                "handelingsPerspectief": "handelingsPerspectief",
                "einddatumHandelingsTermijn": "tests",  # input string
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(
                get_validation_errors(response, "einddatumHandelingsTermijn"),
                {
                    "name": "einddatumHandelingsTermijn",
                    "code": "invalid",
                    "reason": "Datetime heeft een ongeldig formaat, gebruik 1 van de volgende formaten: "
                    "YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].",
                },
            )
            self.assertEqual(ExterneTaak.objects.all().count(), 0)

        with self.subTest("invalid status choice"):
            data = {
                "titel": "TestTitle",
                "handelingsPerspectief": "handelingsPerspectief",
                "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
                "status": "test",  # wrong choice
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "status"),
                {
                    "name": "status",
                    "code": "invalid_choice",
                    "reason": '"test" is een ongeldige keuze.',
                },
            )
            self.assertEqual(ExterneTaak.objects.all().count(), 0)

        with self.subTest("invalid taak_soort choice"):
            data = {
                "titel": "TestTitle",
                "handelingsPerspectief": "handelingsPerspectief",
                "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
                "taakSoort": "test",  # wrong choice
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "taakSoort"),
                {
                    "name": "taakSoort",
                    "code": "invalid_choice",
                    "reason": '"test" is een ongeldige keuze.',
                },
            )
            self.assertEqual(ExterneTaak.objects.all().count(), 0)

    def test_valid_update_partial(self):
        externetaak = ExterneTaakFactory.create()

        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )

        # empty patch
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "uuid": str(externetaak.uuid),
                "titel": externetaak.titel,
                "status": StatusTaak.OPEN.value,  # default value
                "startdatum": externetaak.startdatum,
                "handelingsPerspectief": externetaak.handelings_perspectief,
                "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": externetaak.datum_herinnering,
                "toelichting": externetaak.toelichting,
                "taakSoort": externetaak.taak_soort,
            },
        )

        # status patch
        response = self.client.patch(
            detail_url,
            {
                "titel": "new_titel",
                "status": StatusTaak.VERWERKT.value,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        externetaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "uuid": str(externetaak.uuid),
                "titel": externetaak.titel,
                "status": StatusTaak.VERWERKT.value,  # changed value
                "startdatum": externetaak.startdatum,
                "handelingsPerspectief": externetaak.handelings_perspectief,
                "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": externetaak.datum_herinnering,
                "toelichting": externetaak.toelichting,
                "taakSoort": externetaak.taak_soort,
            },
        )

    def test_valid_update(self):
        externetaak = ExterneTaakFactory.create()

        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )

        # required put
        response = self.client.put(
            detail_url,
            {
                "titel": "new_titel",
                "handelingsPerspectief": "new_handelingsPerspectief",
                "einddatumHandelingsTermijn": "2025-02-02T12:00:00",
            },
        )
        externetaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "uuid": str(externetaak.uuid),
                "titel": externetaak.titel,
                "status": StatusTaak.OPEN.value,
                "startdatum": externetaak.startdatum,
                "handelingsPerspectief": externetaak.handelings_perspectief,
                "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": externetaak.datum_herinnering,
                "toelichting": externetaak.toelichting,
                "taakSoort": externetaak.taak_soort,
            },
        )

    def test_destroy(self):
        externetaak = ExterneTaakFactory.create()
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )

        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
