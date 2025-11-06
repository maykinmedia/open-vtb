import uuid

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


class BetaalTaakTests(APITestCase):
    list_url = reverse("taken:betaaltaken-list")

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        #
        ExterneTaakFactory.create_batch(3)
        self.assertEqual(ExterneTaak.objects.all().count(), 3)
        self.assertEqual(
            ExterneTaak.objects.filter(taak_soort=SoortTaak.BETAALTAAK.value).count(), 0
        )
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)

        # list all sorts of tasks
        ExterneTaakFactory.create(betaaltaak=True)
        ExterneTaakFactory.create(betaaltaak=True)
        ExterneTaakFactory.create(betaaltaak=True)
        self.assertEqual(
            ExterneTaak.objects.filter(taak_soort=SoortTaak.BETAALTAAK.value).count(), 3
        )
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertEqual(ExterneTaak.objects.all().count(), 6)

    def test_detail(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)
        detail_url = reverse(
            "taken:betaaltaken-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "externeTaak": {
                    "uuid": str(betaaltaak.uuid),
                    "titel": betaaltaak.titel,
                    "status": betaaltaak.status,
                    "startdatum": betaaltaak.startdatum,
                    "handelingsPerspectief": betaaltaak.handelings_perspectief,
                    "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat().replace(
                        "+00:00", "Z"
                    ),
                    "datumHerinnering": betaaltaak.datum_herinnering,
                    "toelichting": betaaltaak.toelichting,
                    "taakSoort": SoortTaak.BETAALTAAK.value,
                },
                "bedrag": betaaltaak.data["bedrag"],
                "valuta": betaaltaak.data["valuta"],
                "transactieomschrijving": betaaltaak.data["transactieomschrijving"],
                "doelrekening": {
                    "naam": betaaltaak.data["doelrekening"]["naam"],
                    "iban": betaaltaak.data["doelrekening"]["iban"],
                },
            },
        )

    def test_detail_not_found(self):
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(uuid.uuid4())}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # different taak_soort
        gegevensuitvraagtaak = ExterneTaakFactory.create(gegevensuitvraagtaak=True)
        detail_url = reverse(
            "taken:betaaltaken-detail", kwargs={"uuid": str(gegevensuitvraagtaak.uuid)}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_create(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "externeTaak": {
                "titel": "titel",
                "handelingsPerspectief": "handelingsPerspectief1",
                "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
            },
            "bedrag": "11",
            "valuta": "EUR",
            "transactieomschrijving": "test",
            "doelrekening": {
                "naam": "test",
                "iban": "iban-code-test",
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        betaaltaak = ExterneTaak.objects.get()

        self.assertEqual(
            response.json(),
            {
                "externeTaak": {
                    "uuid": str(betaaltaak.uuid),
                    "titel": betaaltaak.titel,
                    "status": betaaltaak.status,
                    "startdatum": betaaltaak.startdatum,
                    "handelingsPerspectief": betaaltaak.handelings_perspectief,
                    "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat().replace(
                        "+00:00", "Z"
                    ),
                    "datumHerinnering": betaaltaak.datum_herinnering,
                    "toelichting": betaaltaak.toelichting,
                    "taakSoort": SoortTaak.BETAALTAAK.value,
                },
                "bedrag": betaaltaak.data["bedrag"],
                "valuta": betaaltaak.data["valuta"],
                "transactieomschrijving": betaaltaak.data["transactieomschrijving"],
                "doelrekening": {
                    "naam": betaaltaak.data["doelrekening"]["naam"],
                    "iban": betaaltaak.data["doelrekening"]["iban"],
                },
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 4)

        self.assertEqual(
            get_validation_errors(response, "externeTaak"),
            {
                "name": "externeTaak",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "bedrag"),
            {
                "name": "bedrag",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "transactieomschrijving"),
            {
                "name": "transactieomschrijving",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "doelrekening"),
            {
                "name": "doelrekening",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        # externeTaak and doelrekening empty values
        data = {
            "externeTaak": {},
            "bedrag": 11,
            "valuta": "EUR",
            "transactieomschrijving": "test",
            "doelrekening": {},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 5)
        self.assertEqual(
            get_validation_errors(response, "externeTaak.titel"),
            {
                "name": "externeTaak.titel",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "externeTaak.handelingsPerspectief"),
            {
                "name": "externeTaak.handelingsPerspectief",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "externeTaak.einddatumHandelingsTermijn"),
            {
                "name": "externeTaak.einddatumHandelingsTermijn",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "doelrekening.naam"),
            {
                "name": "doelrekening.naam",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "doelrekening.iban"),
            {
                "name": "doelrekening.iban",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_invalid_create_pass_wrong_soort_taak(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "externeTaak": {
                "titel": "titel",
                "handelingsPerspectief": "handelingsPerspectief1",
                "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
                "taakSoort": SoortTaak.FORMULIERTAAK.value,
            },
            "bedrag": "11",
            "valuta": "EUR",
            "transactieomschrijving": "test",
            "doelrekening": {
                "naam": "test",
                "iban": "iban-code-test",
            },
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(
            get_validation_errors(response, "externeTaak.taakSoort"),
            {
                "name": "externeTaak.taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )

    def test_invalid_create_type_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        with self.subTest("invalid bedrag value"):
            data = {
                "externeTaak": {
                    "titel": "titel",
                    "handelingsPerspectief": "handelingsPerspectief1",
                    "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
                },
                "bedrag": "test",  # should be decimal
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "bedrag"),
                {
                    "name": "bedrag",
                    "code": "invalid",
                    "reason": "'test' is not a valid decimal number",
                },
            )
            self.assertEqual(ExterneTaak.objects.all().count(), 0)

        with self.subTest("invalid valuta choice"):
            data = {
                "externeTaak": {
                    "titel": "titel",
                    "handelingsPerspectief": "handelingsPerspectief1",
                    "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
                },
                "bedrag": "11",
                "valuta": "TEST",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "valuta"),
                {
                    "name": "valuta",
                    "code": "invalid_choice",
                    "reason": '"TEST" is een ongeldige keuze.',
                },
            )
            self.assertEqual(ExterneTaak.objects.all().count(), 0)

    def test_valid_update_partial(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaken-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )
        # empty patch
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "externeTaak": {
                    "uuid": str(betaaltaak.uuid),
                    "titel": betaaltaak.titel,
                    "status": betaaltaak.status,
                    "startdatum": betaaltaak.startdatum,
                    "handelingsPerspectief": betaaltaak.handelings_perspectief,
                    "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat().replace(
                        "+00:00", "Z"
                    ),
                    "datumHerinnering": betaaltaak.datum_herinnering,
                    "toelichting": betaaltaak.toelichting,
                    "taakSoort": SoortTaak.BETAALTAAK.value,
                },
                "bedrag": betaaltaak.data["bedrag"],
                "valuta": betaaltaak.data["valuta"],
                "transactieomschrijving": betaaltaak.data["transactieomschrijving"],
                "doelrekening": {
                    "naam": betaaltaak.data["doelrekening"]["naam"],
                    "iban": betaaltaak.data["doelrekening"]["iban"],
                },
            },
        )

        # patch externe_taak field
        response = self.client.patch(
            detail_url, {"externeTaak": {"titel": "new_title"}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(betaaltaak.titel, "new_title")

        # patch one field from json_data
        self.assertEqual(betaaltaak.data["bedrag"], "10.12")  # default factory value
        response = self.client.patch(detail_url, {"bedrag": "100"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(betaaltaak.data["bedrag"], "100")

        # patch one field from json_data
        self.assertEqual(
            betaaltaak.data["doelrekening"],
            {
                "naam": "test",
                "iban": "iban-code-test",
            },
        )  # default factory value
        response = self.client.patch(
            detail_url,
            {
                "doelrekening": {
                    "naam": "new_naam",
                    "iban": "new_iban",
                }
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(
            betaaltaak.data["doelrekening"],
            {
                "naam": "new_naam",
                "iban": "new_iban",
            },
        )

    def test_valid_update(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaken-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )

        # required put
        response = self.client.put(
            detail_url,
            {
                "externeTaak": {
                    "titel": "titel",
                    "handelingsPerspectief": "handelingsPerspectief1",
                    "einddatumHandelingsTermijn": "2025-01-01T12:00:00",
                },
                "bedrag": "100",
                "valuta": "EUR",
                "transactieomschrijving": "new_test",
                "doelrekening": {
                    "naam": "new_test",
                    "iban": "new-iban-code-test",
                },
            },
        )
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "externeTaak": {
                    "uuid": str(betaaltaak.uuid),
                    "titel": betaaltaak.titel,
                    "status": betaaltaak.status,
                    "startdatum": betaaltaak.startdatum,
                    "handelingsPerspectief": betaaltaak.handelings_perspectief,
                    "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat().replace(
                        "+00:00", "Z"
                    ),
                    "datumHerinnering": betaaltaak.datum_herinnering,
                    "toelichting": betaaltaak.toelichting,
                    "taakSoort": SoortTaak.BETAALTAAK.value,
                },
                "bedrag": betaaltaak.data["bedrag"],
                "valuta": betaaltaak.data["valuta"],
                "transactieomschrijving": betaaltaak.data["transactieomschrijving"],
                "doelrekening": {
                    "naam": betaaltaak.data["doelrekening"]["naam"],
                    "iban": betaaltaak.data["doelrekening"]["iban"],
                },
            },
        )

    def test_destroy(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaken-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )

        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
