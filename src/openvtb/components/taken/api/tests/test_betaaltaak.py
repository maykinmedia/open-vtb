import datetime
import uuid

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


class BetaalTaakTests(APITestCase):
    list_url = reverse("taken:betaaltaak-list")

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        # create 1 betaaltaak
        ExterneTaakFactory.create(betaaltaak=True)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        betaaltaak = ExterneTaak.objects.get()

        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(betaaltaak.uuid)})}",
                        "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                        "uuid": str(betaaltaak.uuid),
                        "titel": betaaltaak.titel,
                        "status": betaaltaak.status,
                        "startdatum": betaaltaak.startdatum.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "handelingsPerspectief": betaaltaak.handelings_perspectief,
                        "einddatumHandelingsTermijn": betaaltaak.einddatum_handelings_termijn.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "datumHerinnering": betaaltaak.datum_herinnering,
                        "toelichting": betaaltaak.toelichting,
                        "partijIsToegewezenAan": "",
                        "medewerkerWordtBehandeldDoor": "",
                        "zaakHoortBij": "",
                        "productHeeftBetrekkingOp": "",
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
                ],
            },
        )

        # create 1 gegevensuitvraagtaak
        ExterneTaakFactory.create(gegevensuitvraagtaak=True)

        # assert only 1 betaaltaak
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["uuid"], str(betaaltaak.uuid))

        # assert 2 total externeTaak
        self.assertEqual(ExterneTaak.objects.all().count(), 2)

    def test_detail(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)
        detail_url = reverse(
            "taken:betaaltaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(betaaltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": betaaltaak.status,
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

    def test_detail_not_found(self):
        # random uuid
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(uuid.uuid4())}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # different taak_soort
        gegevensuitvraagtaak = ExterneTaakFactory.create(gegevensuitvraagtaak=True)
        detail_url = reverse(
            "taken:betaaltaak-detail", kwargs={"uuid": str(gegevensuitvraagtaak.uuid)}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_create(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief1",
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
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
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
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
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
            get_validation_errors(response, "details"),
            {
                "name": "details",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(ExterneTaak.objects.all().count(), 0)

        # empty details values
        data = {
            "titel": "test",
            "handelingsPerspectief": "test",
            "details": {},
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
        # details.doelrekening empty values
        data = {
            "titel": "test",
            "handelingsPerspectief": "test",
            "details": {
                "bedrag": "12",
                "transactieomschrijving": "12",
                "doelrekening": {},
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 2)
        self.assertEqual(
            get_validation_errors(response, "details.doelrekening.naam"),
            {
                "name": "details.doelrekening.naam",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "details.doelrekening.iban"),
            {
                "name": "details.doelrekening.iban",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_valid_update_partial(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
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
                "status": betaaltaak.status,
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

        # patch externe_taak field
        response = self.client.patch(detail_url, {"titel": "new_title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(betaaltaak.titel, "new_title")

        # patch one field from json_data
        self.assertEqual(betaaltaak.details["bedrag"], "10.12")  # default factory value
        response = self.client.patch(
            detail_url,
            {
                "details": {
                    "bedrag": "100",
                }
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(betaaltaak.details["bedrag"], "100")

        # patch one field from json_data
        self.assertEqual(
            betaaltaak.details["doelrekening"],
            {
                "naam": "test",
                "iban": "NL18BANK23481326",
            },
        )  # default factory value
        response = self.client.patch(
            detail_url,
            {
                "details": {
                    "doelrekening": {
                        "naam": "new_naam",
                        "iban": "NL18BANK23481111",  # new iban
                    }
                }
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        betaaltaak = ExterneTaak.objects.get()
        self.assertEqual(
            betaaltaak.details["doelrekening"],
            {
                "naam": "new_naam",
                "iban": "NL18BANK23481111",
            },
        )

    def test_valid_update(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )

        # all required PUT fields
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(betaaltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(betaaltaak.uuid)}",
                "uuid": str(betaaltaak.uuid),
                "titel": betaaltaak.titel,
                "status": betaaltaak.status,
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

    def test_invalid_update_required(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )

        # all required PUT fields
        response = self.client.put(detail_url, {})
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
            get_validation_errors(response, "details"),
            {
                "name": "details",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_destroy(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )

        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertEqual(ExterneTaak.objects.all().count(), 0)


class BetaalTaakValidationTests(APITestCase):
    list_url = reverse("taken:betaaltaak-list")

    def test_invalid_create_pass_soort_taak(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        # wrong soort_taak
        data = {
            "titel": "test",
            "handelingsPerspectief": "test",
            "taakSoort": SoortTaak.FORMULIERTAAK.value,
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
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )
        # same soort_taak
        data["taakSoort"] = SoortTaak.BETAALTAAK.value
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )

    def test_invalid_update_partial(self):
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)

        detail_url = reverse(
            "taken:betaaltaak-detail", kwargs={"uuid": str(betaaltaak.uuid)}
        )
        # pass taak_soort
        response = self.client.patch(
            detail_url, {"taakSoort": SoortTaak.FORMULIERTAAK.value}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )

    def test_invalid_create_type_fields(self):
        self.assertEqual(ExterneTaak.objects.all().count(), 0)
        with self.subTest("invalid start_date gt end_date"):
            data = {
                "titel": "test",
                "handelingsPerspectief": "test",
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

        with self.subTest("invalid iban format"):
            data = {
                "titel": "test",
                "handelingsPerspectief": "test",
                "details": {
                    "bedrag": "11",
                    "transactieomschrijving": "test",
                    "doelrekening": {
                        "naam": "test",
                        "iban": "test",
                    },
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.doelrekening.iban"),
                {
                    "name": "details.doelrekening.iban",
                    "code": "invalid",
                    "reason": "'test' is not a valid IBAN",
                },
            )
            self.assertEqual(ExterneTaak.objects.all().count(), 0)

        with self.subTest("invalid pass valuta"):
            data = {
                "titel": "test",
                "handelingsPerspectief": "test",
                "details": {
                    "bedrag": "11",
                    "valuta": "ABC",  # different valuta
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
                get_validation_errors(response, "details.valuta"),
                {
                    "name": "details.valuta",
                    "code": "invalid",
                    "reason": "Het is niet toegestaan een andere waarde dan EUR door te geven.",
                },
            )
            self.assertEqual(ExterneTaak.objects.all().count(), 0)
