import datetime

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-01-01")
class ExterneTaakTests(APITestCase):
    list_url = reverse("taken:externetaak-list")

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(ExterneTaak.objects.exists())

        # create taak
        ExterneTaakFactory.create(betaaltaak=True)
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
                        "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(externetaak.uuid)})}",
                        "urn": f"urn:maykin:taken:externetaak:{str(externetaak.uuid)}",
                        "uuid": str(externetaak.uuid),
                        "titel": externetaak.titel,
                        "status": externetaak.status,
                        "verwerkerTaakId": externetaak.verwerker_taak_id,
                        "startdatum": externetaak.startdatum.isoformat(),
                        "handelingsPerspectief": externetaak.handelings_perspectief,
                        "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat(),
                        "datumHerinnering": externetaak.datum_herinnering.isoformat(),
                        "toelichting": externetaak.toelichting,
                        "isToegewezenAan": externetaak.is_toegewezen_aan,
                        "isGerelateerdAan": externetaak.is_gerelateerd_aan,
                        "taakSoort": externetaak.taak_soort,
                        "details": externetaak.details,
                    }
                ],
            },
        )

        # list all sorts of tasks
        ExterneTaakFactory.create(betaaltaak=True)
        ExterneTaakFactory.create(urltaak=True)
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
        externetaak = ExterneTaakFactory.create(betaaltaak=True)
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(externetaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(externetaak.uuid)}",
                "uuid": str(externetaak.uuid),
                "titel": externetaak.titel,
                "status": externetaak.status,
                "verwerkerTaakId": externetaak.verwerker_taak_id,
                "startdatum": externetaak.startdatum.isoformat(),
                "handelingsPerspectief": externetaak.handelings_perspectief,
                "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": externetaak.datum_herinnering.isoformat(),
                "toelichting": externetaak.toelichting,
                "isToegewezenAan": externetaak.is_toegewezen_aan,
                "isGerelateerdAan": externetaak.is_gerelateerd_aan,
                "taakSoort": externetaak.taak_soort,
                "details": externetaak.details,
            },
        )

    def test_valid_create(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "verwerkerTaakId": "123456",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "details": {
                "bedrag": "11",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL12BANK34567890",
                },
            },
            "isToegewezenAan": "urn:example:12345",
            "isGerelateerdAan": [
                {"urn": "urn:nld:gemeenteutrecht:zaak:zaaknummer:00011111"},
                {"urn": "urn:nld:gemeenteutrecht:zaak:zaaknummer:00022222"},
            ],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(betaaltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": betaaltaak.status,
                "verwerkerTaakId": betaaltaak.verwerker_taak_id,
                "startdatum": betaaltaak.startdatum.isoformat(),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": betaaltaak.datum_herinnering.isoformat(),
                "toelichting": betaaltaak.toelichting,
                "isToegewezenAan": betaaltaak.is_toegewezen_aan,
                "isGerelateerdAan": betaaltaak.is_gerelateerd_aan,
                "taakSoort": betaaltaak.taak_soort,
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
                        "code": betaaltaak.details["doelrekening"]["code"],
                        "iban": betaaltaak.details["doelrekening"]["iban"],
                    },
                },
            },
        )

        # test datumHerinnering auto filled
        # einddatumHandelingsTermijn - TAKEN_DEFAULT_REMINDER_IN_DAYS(7 days)
        self.assertEqual(betaaltaak.datum_herinnering, datetime.date(2026, 1, 3))

    def test_valid_create_with_external_relations(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "details": {
                "bedrag": "11",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL12BANK34567890",
                },
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(betaaltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": betaaltaak.status,
                "verwerkerTaakId": betaaltaak.verwerker_taak_id,
                "startdatum": betaaltaak.startdatum.isoformat(),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": betaaltaak.datum_herinnering.isoformat(),
                "toelichting": betaaltaak.toelichting,
                "taakSoort": betaaltaak.taak_soort,
                "isToegewezenAan": betaaltaak.is_toegewezen_aan,
                "isGerelateerdAan": betaaltaak.is_gerelateerd_aan,
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
                        "code": betaaltaak.details["doelrekening"]["code"],
                        "iban": betaaltaak.details["doelrekening"]["iban"],
                    },
                },
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 4)
        self.assertEqual(
            get_validation_errors(response, "titel"),
            {
                "name": "titel",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
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
        self.assertEqual(
            get_validation_errors(response, "details"),
            {
                "name": "details",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertFalse(ExterneTaak.objects.exists())

        # invalid taakSoort value
        data = {
            "titel": "test",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": "test",
            "details": {},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid_choice",
                "reason": '"test" is een ongeldige keuze.',
            },
        )

        # empty taakSoort value
        data = {
            "titel": "test",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": "",
            "details": {},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid_choice",
                "reason": '"" is een ongeldige keuze.',
            },
        )

        # invalid details schema
        data = {
            "titel": "test",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "details": {
                "uitvraagLink": "http://example.com/",
                "ontvangenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                    },
                },
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 3)
        self.assertEqual(
            get_validation_errors(response, "details.bedrag"),
            {
                "name": "details.bedrag",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "details.transactieomschrijving"),
            {
                "name": "details.transactieomschrijving",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "details.doelrekening"),
            {
                "name": "details.doelrekening",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_update_partial(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )
        # empty PATCH
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(betaaltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": str(betaaltaak.status),
                "verwerkerTaakId": betaaltaak.verwerker_taak_id,
                "startdatum": betaaltaak.startdatum.isoformat(),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": betaaltaak.datum_herinnering.isoformat(),
                "toelichting": betaaltaak.toelichting,
                "isToegewezenAan": betaaltaak.is_toegewezen_aan,
                "isGerelateerdAan": betaaltaak.is_gerelateerd_aan,
                "taakSoort": str(betaaltaak.taak_soort),
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
                        "code": betaaltaak.details["doelrekening"]["code"],
                        "iban": betaaltaak.details["doelrekening"]["iban"],
                    },
                },
            },
        )

        # patch externe_taak field
        response = self.client.patch(detail_url, {"titel": "new_title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(betaaltaak.titel, "new_title")

        # patch taakSoort with wrong details
        response = self.client.patch(
            detail_url, {"taak_soort": SoortTaak.URLTAAK.value}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "details"),
            {
                "name": "details",
                "code": "invalid",
                "reason": "'uitvraagLink' is a required property",
            },
        )

        # patch taakSoort with the new details
        response = self.client.patch(
            detail_url,
            {
                "taak_soort": SoortTaak.URLTAAK.value,
                "details": {"uitvraagLink": "http://example.com/"},
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(urltaak.taak_soort, SoortTaak.URLTAAK.value)
        self.assertEqual(
            urltaak.details,
            {"uitvraagLink": "http://example.com/"},
        )

        # patch isToegewezenAan with the new details
        response = self.client.patch(
            detail_url,
            {"isToegewezenAan": "urn:example:12345"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(urltaak.is_toegewezen_aan, "urn:example:12345")

        # patch isGerelateerdAan with the new details
        response = self.client.patch(
            detail_url,
            {
                "isGerelateerdAan": [
                    {"urn": "urn:nld:test1:12345"},
                    {"urn": "urn:nld:test2:67890"},
                ],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(
            urltaak.is_gerelateerd_aan,
            [{"urn": "urn:nld:test1:12345"}, {"urn": "urn:nld:test2:67890"}],
        )

    def test_update(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )

        # all required PUT fields
        response = self.client.put(
            detail_url,
            {
                "titel": "new_titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taak_soort": SoortTaak.BETAALTAAK.value,
                "details": {
                    "bedrag": "100",
                    "valuta": "EUR",
                    "transactieomschrijving": "new_test",
                    "doelrekening": {
                        "naam": "new_test",
                        "code": "123-ABC",
                        "iban": "NL18BANK23481111",  # new iban
                    },
                },
            },
        )
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(betaaltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": str(betaaltaak.status),
                "verwerkerTaakId": betaaltaak.verwerker_taak_id,
                "startdatum": betaaltaak.startdatum.isoformat(),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": betaaltaak.datum_herinnering.isoformat(),
                "toelichting": betaaltaak.toelichting,
                "isToegewezenAan": betaaltaak.is_toegewezen_aan,
                "isGerelateerdAan": betaaltaak.is_gerelateerd_aan,
                "taakSoort": str(betaaltaak.taak_soort),
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
                        "code": betaaltaak.details["doelrekening"]["code"],
                        "iban": betaaltaak.details["doelrekening"]["iban"],
                    },
                },
            },
        )

        # taakSoort required
        response = self.client.put(
            detail_url,
            {
                "titel": "new_titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "bedrag": "100",
                    "valuta": "EUR",
                    "transactieomschrijving": "new_test",
                    "doelrekening": {
                        "naam": "new_test",
                        "code": "123-ABC",
                        "iban": "NL18BANK23481111",  # new iban
                    },
                },
            },
        )
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

        # change taak_soort
        response = self.client.put(
            detail_url,
            {
                "titel": "new_titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "taakSoort": SoortTaak.URLTAAK.value,
                "details": {"uitvraagLink": "http://example.com/"},
            },
        )
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(urltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                "uuid": str(urltaak.uuid),
                "titel": urltaak.titel,
                "status": str(urltaak.status),
                "verwerkerTaakId": urltaak.verwerker_taak_id,
                "startdatum": urltaak.startdatum.isoformat(),
                "handelingsPerspectief": urltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": urltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": urltaak.datum_herinnering.isoformat(),
                "toelichting": urltaak.toelichting,
                "isToegewezenAan": betaaltaak.is_toegewezen_aan,
                "isGerelateerdAan": betaaltaak.is_gerelateerd_aan,
                "taakSoort": str(urltaak.taak_soort),
                "details": urltaak.details,
            },
        )

    def test_destroy(self):
        externetaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )

        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(ExterneTaak.objects.exists())
