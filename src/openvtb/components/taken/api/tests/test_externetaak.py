import datetime

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
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
                        "uuid": str(externetaak.uuid),
                        "titel": externetaak.titel,
                        "status": externetaak.status,
                        "startdatum": externetaak.startdatum.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "handelingsPerspectief": externetaak.handelings_perspectief,
                        "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "datumHerinnering": externetaak.datum_herinnering,
                        "toelichting": externetaak.toelichting,
                        "partijIsToegewezenAan": "",
                        "medewerkerWordtBehandeldDoor": "",
                        "zaakHoortBij": "",
                        "productHeeftBetrekkingOp": "",
                        "taakSoort": externetaak.taak_soort,
                        "details": externetaak.details,
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
                "uuid": str(externetaak.uuid),
                "titel": externetaak.titel,
                "status": externetaak.status,
                "startdatum": externetaak.startdatum.isoformat().replace("+00:00", "Z"),
                "handelingsPerspectief": externetaak.handelings_perspectief,
                "einddatumHandelingsTermijn": externetaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": externetaak.datum_herinnering,
                "toelichting": externetaak.toelichting,
                "partijIsToegewezenAan": externetaak.partij_is_toegewezen_aan,
                "medewerkerWordtBehandeldDoor": externetaak.medewerker_wordt_behandeld_door,
                "zaakHoortBij": externetaak.zaak_hoort_bij,
                "productHeeftBetrekkingOp": externetaak.product_heeft_betrekking_op,
                "taakSoort": externetaak.taak_soort,
                "details": externetaak.details,
            },
        )

    def test_valid_create(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief1",
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "details": {
                "bedrag": "11",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "NL18BANK23481326",
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
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": betaaltaak.status,
                "startdatum": betaaltaak.startdatum.isoformat().replace("+00:00", "Z"),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": None,
                "datumHerinnering": betaaltaak.datum_herinnering,
                "toelichting": betaaltaak.toelichting,
                "partijIsToegewezenAan": betaaltaak.partij_is_toegewezen_aan,
                "medewerkerWordtBehandeldDoor": betaaltaak.medewerker_wordt_behandeld_door,
                "zaakHoortBij": betaaltaak.zaak_hoort_bij,
                "productHeeftBetrekkingOp": betaaltaak.product_heeft_betrekking_op,
                "taakSoort": betaaltaak.taak_soort,
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
                        "iban": betaaltaak.details["doelrekening"]["iban"],
                    },
                },
            },
        )

    def test_valid_create_with_external_relations(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief1",
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "partijIsToegewezenAan": "urn:maykin:partij:brp:nnp:bsn:1234567892",
            "medewerkerWordtBehandeldDoor": "urn:maykin:medewerker:brp:nnp:bsn:1234567892",
            "zaakHoortBij": "urn:maykin:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "productHeeftBetrekkingOp": "urn:maykin:product:cec996f4-2efa-4307-a035-32c2c9032e89",
            "details": {
                "bedrag": "11",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "NL18BANK23481326",
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
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": betaaltaak.status,
                "startdatum": betaaltaak.startdatum.isoformat().replace("+00:00", "Z"),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": None,
                "datumHerinnering": betaaltaak.datum_herinnering,
                "toelichting": betaaltaak.toelichting,
                "partijIsToegewezenAan": betaaltaak.partij_is_toegewezen_aan,
                "medewerkerWordtBehandeldDoor": betaaltaak.medewerker_wordt_behandeld_door,
                "zaakHoortBij": betaaltaak.zaak_hoort_bij,
                "productHeeftBetrekkingOp": betaaltaak.product_heeft_betrekking_op,
                "taakSoort": betaaltaak.taak_soort,
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
                        "iban": betaaltaak.details["doelrekening"]["iban"],
                    },
                },
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        details = {}
        response = self.client.post(self.list_url, details)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
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
            get_validation_errors(response, "handelingsPerspectief"),
            {
                "name": "handelingsPerspectief",
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
            get_validation_errors(response, "details"),
            {
                "name": "details",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        # invalid taakSoort value
        data = {
            "titel": "test",
            "handelingsPerspectief": "test",
            "taakSoort": "test",
            "details": {},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
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
            "handelingsPerspectief": "test",
            "taakSoort": "",
            "details": {},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
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
            "handelingsPerspectief": "test",
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
        self.assertEqual(response.data["title"], "Invalid input.")
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
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": str(betaaltaak.status),
                "startdatum": betaaltaak.startdatum.isoformat().replace("+00:00", "Z"),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": betaaltaak.datum_herinnering,
                "toelichting": betaaltaak.toelichting,
                "partijIsToegewezenAan": betaaltaak.partij_is_toegewezen_aan,
                "medewerkerWordtBehandeldDoor": betaaltaak.medewerker_wordt_behandeld_door,
                "zaakHoortBij": betaaltaak.zaak_hoort_bij,
                "productHeeftBetrekkingOp": betaaltaak.product_heeft_betrekking_op,
                "taakSoort": str(betaaltaak.taak_soort),
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
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
            detail_url, {"taak_soort": SoortTaak.GEGEVENSUITVRAAGTAAK.value}
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
                "taak_soort": SoortTaak.GEGEVENSUITVRAAGTAAK.value,
                "details": {"uitvraagLink": "http://example.com/"},
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(
            gegevensuitvraagtaak.taak_soort, SoortTaak.GEGEVENSUITVRAAGTAAK.value
        )
        self.assertEqual(
            gegevensuitvraagtaak.details,
            {"uitvraagLink": "http://example.com/"},
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
                "handelingsPerspectief": "new_handelingsPerspectief",
                "taak_soort": SoortTaak.BETAALTAAK.value,
                "details": {
                    "bedrag": "100",
                    "valuta": "EUR",
                    "transactieomschrijving": "new_test",
                    "doelrekening": {
                        "naam": "new_test",
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
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": str(betaaltaak.status),
                "startdatum": betaaltaak.startdatum.isoformat().replace("+00:00", "Z"),
                "handelingsPerspectief": betaaltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": betaaltaak.datum_herinnering,
                "toelichting": betaaltaak.toelichting,
                "partijIsToegewezenAan": betaaltaak.partij_is_toegewezen_aan,
                "medewerkerWordtBehandeldDoor": betaaltaak.medewerker_wordt_behandeld_door,
                "zaakHoortBij": betaaltaak.zaak_hoort_bij,
                "productHeeftBetrekkingOp": betaaltaak.product_heeft_betrekking_op,
                "taakSoort": str(betaaltaak.taak_soort),
                "details": {
                    "bedrag": betaaltaak.details["bedrag"],
                    "valuta": betaaltaak.details["valuta"],
                    "transactieomschrijving": betaaltaak.details[
                        "transactieomschrijving"
                    ],
                    "doelrekening": {
                        "naam": betaaltaak.details["doelrekening"]["naam"],
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
                "handelingsPerspectief": "new_handelingsPerspectief",
                "details": {
                    "bedrag": "100",
                    "valuta": "EUR",
                    "transactieomschrijving": "new_test",
                    "doelrekening": {
                        "naam": "new_test",
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
                "handelingsPerspectief": "new_handelingsPerspectief",
                "taakSoort": SoortTaak.GEGEVENSUITVRAAGTAAK.value,
                "details": {"uitvraagLink": "http://example.com/"},
            },
        )
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(gegevensuitvraagtaak.uuid)})}",
                "uuid": str(gegevensuitvraagtaak.uuid),
                "titel": gegevensuitvraagtaak.titel,
                "status": str(gegevensuitvraagtaak.status),
                "startdatum": gegevensuitvraagtaak.startdatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "handelingsPerspectief": gegevensuitvraagtaak.handelings_perspectief,
                "einddatumHandelingsTermijn": gegevensuitvraagtaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": gegevensuitvraagtaak.datum_herinnering,
                "toelichting": gegevensuitvraagtaak.toelichting,
                "partijIsToegewezenAan": betaaltaak.partij_is_toegewezen_aan,
                "medewerkerWordtBehandeldDoor": betaaltaak.medewerker_wordt_behandeld_door,
                "zaakHoortBij": betaaltaak.zaak_hoort_bij,
                "productHeeftBetrekkingOp": betaaltaak.product_heeft_betrekking_op,
                "taakSoort": str(gegevensuitvraagtaak.taak_soort),
                "details": gegevensuitvraagtaak.details,
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
        self.assertEqual(ExterneTaak.objects.all().count(), 0)


class ExterneTaakValidationTests(APITestCase):
    list_url = reverse("taken:externetaak-list")

    def test_invalid_create_type_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "titel": "test",
            "handelingsPerspectief": "test",
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "startdatum": datetime.datetime(2025, 1, 1, 10, 0, 0),  # end < start
            "einddatumHandelingsTermijn": datetime.datetime(2024, 1, 1, 10, 0, 0),
            "details": {
                "bedrag": "11",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "NL18BANK23481326",
                },
            },
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
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

    def test_invalid_create_urn_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief1",
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "partijIsToegewezenAan": "test",
            "medewerkerWordtBehandeldDoor": "test:maykin:medewerker:brp:nnp:bsn:1234567892",  # doesn't start with urn
            "zaakHoortBij": "urn:maykinmaykinmaykinmaykinmaykinmaykinmaykinmaykinmaykin:1",  # long NID
            "details": {
                "bedrag": "11",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "NL18BANK23481326",
                },
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "partijIsToegewezenAan"),
            {
                "name": "partijIsToegewezenAan",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "medewerkerWordtBehandeldDoor"),
            {
                "name": "medewerkerWordtBehandeldDoor",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "zaakHoortBij"),
            {
                "name": "zaakHoortBij",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
