import datetime
import uuid

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


class GegevensuitvraagTaakTests(APITestCase):
    list_url = reverse("taken:gegevensuitvraagtaak-list")

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(ExterneTaak.objects.exists())

        # create 1 gegevensuitvraagtaak
        ExterneTaakFactory.create(gegevensuitvraagtaak=True)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(gegevensuitvraagtaak.uuid)})}",
                        "urn": f"urn:maykin:taken:externetaak:{str(gegevensuitvraagtaak.uuid)}",
                        "uuid": str(gegevensuitvraagtaak.uuid),
                        "titel": gegevensuitvraagtaak.titel,
                        "status": gegevensuitvraagtaak.status,
                        "startdatum": gegevensuitvraagtaak.startdatum.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "handelingsPerspectief": gegevensuitvraagtaak.handelings_perspectief,
                        "einddatumHandelingsTermijn": gegevensuitvraagtaak.einddatum_handelings_termijn.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "datumHerinnering": gegevensuitvraagtaak.datum_herinnering,
                        "toelichting": gegevensuitvraagtaak.toelichting,
                        "isToegewezenAanPartij": "",
                        "wordtBehandeldDoorMedewerker": "",
                        "hoortBijZaak": "",
                        "heeftBetrekkingOpProduct": "",
                        "taakSoort": gegevensuitvraagtaak.taak_soort,
                        "details": {
                            "uitvraagLink": gegevensuitvraagtaak.details[
                                "uitvraagLink"
                            ],
                            "ontvangenGegevens": gegevensuitvraagtaak.details[
                                "ontvangenGegevens"
                            ],
                        },
                    },
                ],
            },
        )

        # create 1 betaaltaak
        ExterneTaakFactory.create(betaaltaak=True)

        # assert only 1 gegevensuitvraagtaak
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(
            response.json()["results"][0]["uuid"],
            str(gegevensuitvraagtaak.uuid),
        )

        # assert 2 total externeTaak
        self.assertEqual(ExterneTaak.objects.all().count(), 2)

    def test_detail(self):
        gegevensuitvraagtaak = ExterneTaakFactory.create(gegevensuitvraagtaak=True)
        detail_url = reverse(
            "taken:gegevensuitvraagtaak-detail",
            kwargs={"uuid": str(gegevensuitvraagtaak.uuid)},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(gegevensuitvraagtaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(gegevensuitvraagtaak.uuid)}",
                "uuid": str(gegevensuitvraagtaak.uuid),
                "titel": gegevensuitvraagtaak.titel,
                "status": gegevensuitvraagtaak.status,
                "startdatum": gegevensuitvraagtaak.startdatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "handelingsPerspectief": gegevensuitvraagtaak.handelings_perspectief,
                "einddatumHandelingsTermijn": gegevensuitvraagtaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": gegevensuitvraagtaak.datum_herinnering,
                "toelichting": gegevensuitvraagtaak.toelichting,
                "isToegewezenAanPartij": gegevensuitvraagtaak.is_toegewezen_aan_partij,
                "wordtBehandeldDoorMedewerker": gegevensuitvraagtaak.wordt_behandeld_door_medewerker,
                "hoortBijZaak": gegevensuitvraagtaak.hoort_bij_zaak,
                "heeftBetrekkingOpProduct": gegevensuitvraagtaak.heeft_betrekking_op_product,
                "taakSoort": gegevensuitvraagtaak.taak_soort,
                "details": {
                    "uitvraagLink": gegevensuitvraagtaak.details["uitvraagLink"],
                    "ontvangenGegevens": gegevensuitvraagtaak.details[
                        "ontvangenGegevens"
                    ],
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
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)
        detail_url = reverse(
            "taken:gegevensuitvraagtaak-detail",
            kwargs={"uuid": str(betaaltaak.uuid)},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_create(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief",
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(gegevensuitvraagtaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(gegevensuitvraagtaak.uuid)}",
                "uuid": str(gegevensuitvraagtaak.uuid),
                "titel": gegevensuitvraagtaak.titel,
                "status": gegevensuitvraagtaak.status,
                "startdatum": gegevensuitvraagtaak.startdatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "handelingsPerspectief": gegevensuitvraagtaak.handelings_perspectief,
                "einddatumHandelingsTermijn": None,
                "datumHerinnering": gegevensuitvraagtaak.datum_herinnering,
                "toelichting": gegevensuitvraagtaak.toelichting,
                "isToegewezenAanPartij": gegevensuitvraagtaak.is_toegewezen_aan_partij,
                "wordtBehandeldDoorMedewerker": gegevensuitvraagtaak.wordt_behandeld_door_medewerker,
                "hoortBijZaak": gegevensuitvraagtaak.hoort_bij_zaak,
                "heeftBetrekkingOpProduct": gegevensuitvraagtaak.heeft_betrekking_op_product,
                "taakSoort": gegevensuitvraagtaak.taak_soort,
                "details": {
                    "uitvraagLink": gegevensuitvraagtaak.details["uitvraagLink"],
                    "ontvangenGegevens": gegevensuitvraagtaak.details[
                        "ontvangenGegevens"
                    ],
                },
            },
        )

        # no ontvangenGegevens key
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief",
            "details": {
                "uitvraagLink": "http://example.com/",
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 2)
        gegevensuitvraagtaak = ExterneTaak.objects.get(uuid=response.json()["uuid"])
        self.assertEqual(gegevensuitvraagtaak.details["ontvangenGegevens"], {})

        # empty value ontvangenGegevens
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief",
            "details": {
                "uitvraagLink": "http://example.com/",
                "ontvangenGegevens": {},
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 3)
        gegevensuitvraagtaak = ExterneTaak.objects.get(uuid=response.json()["uuid"])
        self.assertEqual(gegevensuitvraagtaak.details["ontvangenGegevens"], {})

    def test_valid_create_with_external_relations(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief",
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(gegevensuitvraagtaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(gegevensuitvraagtaak.uuid)}",
                "uuid": str(gegevensuitvraagtaak.uuid),
                "titel": gegevensuitvraagtaak.titel,
                "status": gegevensuitvraagtaak.status,
                "startdatum": gegevensuitvraagtaak.startdatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "handelingsPerspectief": gegevensuitvraagtaak.handelings_perspectief,
                "einddatumHandelingsTermijn": None,
                "datumHerinnering": gegevensuitvraagtaak.datum_herinnering,
                "toelichting": gegevensuitvraagtaak.toelichting,
                "isToegewezenAanPartij": gegevensuitvraagtaak.is_toegewezen_aan_partij,
                "wordtBehandeldDoorMedewerker": gegevensuitvraagtaak.wordt_behandeld_door_medewerker,
                "hoortBijZaak": gegevensuitvraagtaak.hoort_bij_zaak,
                "heeftBetrekkingOpProduct": gegevensuitvraagtaak.heeft_betrekking_op_product,
                "taakSoort": gegevensuitvraagtaak.taak_soort,
                "details": {
                    "uitvraagLink": gegevensuitvraagtaak.details["uitvraagLink"],
                    "ontvangenGegevens": gegevensuitvraagtaak.details[
                        "ontvangenGegevens"
                    ],
                },
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
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
        self.assertFalse(ExterneTaak.objects.exists())

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
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "details.uitvraagLink"),
            {
                "name": "details.uitvraagLink",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertFalse(ExterneTaak.objects.exists())

    def test_valid_update_partial(self):
        gegevensuitvraagtaak = ExterneTaakFactory.create(gegevensuitvraagtaak=True)

        detail_url = reverse(
            "taken:gegevensuitvraagtaak-detail",
            kwargs={"uuid": str(gegevensuitvraagtaak.uuid)},
        )
        # empty PATCH
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(gegevensuitvraagtaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(gegevensuitvraagtaak.uuid)}",
                "uuid": str(gegevensuitvraagtaak.uuid),
                "titel": gegevensuitvraagtaak.titel,
                "status": gegevensuitvraagtaak.status,
                "startdatum": gegevensuitvraagtaak.startdatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "handelingsPerspectief": gegevensuitvraagtaak.handelings_perspectief,
                "einddatumHandelingsTermijn": gegevensuitvraagtaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": gegevensuitvraagtaak.datum_herinnering,
                "toelichting": gegevensuitvraagtaak.toelichting,
                "isToegewezenAanPartij": gegevensuitvraagtaak.is_toegewezen_aan_partij,
                "wordtBehandeldDoorMedewerker": gegevensuitvraagtaak.wordt_behandeld_door_medewerker,
                "hoortBijZaak": gegevensuitvraagtaak.hoort_bij_zaak,
                "heeftBetrekkingOpProduct": gegevensuitvraagtaak.heeft_betrekking_op_product,
                "taakSoort": gegevensuitvraagtaak.taak_soort,
                "details": {
                    "uitvraagLink": gegevensuitvraagtaak.details["uitvraagLink"],
                    "ontvangenGegevens": gegevensuitvraagtaak.details[
                        "ontvangenGegevens"
                    ],
                },
            },
        )

        # patch externe_taak field
        response = self.client.patch(detail_url, {"titel": "new_title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(gegevensuitvraagtaak.titel, "new_title")

        # patch one field from json_data
        self.assertEqual(
            gegevensuitvraagtaak.details["uitvraagLink"], "http://example.com/"
        )  # default factory value
        response = self.client.patch(
            detail_url, {"details": {"uitvraagLink": "http://example-new-url.com/"}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(
            gegevensuitvraagtaak.details["uitvraagLink"], "http://example-new-url.com/"
        )

        # update ontvangenGegevens
        self.assertEqual(
            gegevensuitvraagtaak.details["ontvangenGegevens"], {"key": "value"}
        )  # default
        response = self.client.patch(
            detail_url, {"details": {"ontvangenGegevens": {"new_key": "new_value"}}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        # new value
        self.assertEqual(
            gegevensuitvraagtaak.details["ontvangenGegevens"], {"new_key": "new_value"}
        )
        self.assertNotEqual(
            gegevensuitvraagtaak.details["ontvangenGegevens"], {"key": "value"}
        )

    def test_valid_update(self):
        gegevensuitvraagtaak = ExterneTaakFactory.create(gegevensuitvraagtaak=True)

        detail_url = reverse(
            "taken:gegevensuitvraagtaak-detail",
            kwargs={"uuid": str(gegevensuitvraagtaak.uuid)},
        )

        # all required PUT fields
        response = self.client.put(
            detail_url,
            {
                "titel": "titel",
                "handelingsPerspectief": "handelingsPerspectief1",
                "details": {
                    "uitvraagLink": "http://example-new-url.com/",
                },
            },
        )
        gegevensuitvraagtaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(gegevensuitvraagtaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(gegevensuitvraagtaak.uuid)}",
                "uuid": str(gegevensuitvraagtaak.uuid),
                "titel": gegevensuitvraagtaak.titel,
                "status": gegevensuitvraagtaak.status,
                "startdatum": gegevensuitvraagtaak.startdatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "handelingsPerspectief": gegevensuitvraagtaak.handelings_perspectief,
                "einddatumHandelingsTermijn": gegevensuitvraagtaak.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "datumHerinnering": gegevensuitvraagtaak.datum_herinnering,
                "toelichting": gegevensuitvraagtaak.toelichting,
                "isToegewezenAanPartij": gegevensuitvraagtaak.is_toegewezen_aan_partij,
                "wordtBehandeldDoorMedewerker": gegevensuitvraagtaak.wordt_behandeld_door_medewerker,
                "hoortBijZaak": gegevensuitvraagtaak.hoort_bij_zaak,
                "heeftBetrekkingOpProduct": gegevensuitvraagtaak.heeft_betrekking_op_product,
                "taakSoort": gegevensuitvraagtaak.taak_soort,
                "details": {
                    "uitvraagLink": gegevensuitvraagtaak.details["uitvraagLink"],
                    "ontvangenGegevens": gegevensuitvraagtaak.details[
                        "ontvangenGegevens"
                    ],
                },
            },
        )
        self.assertEqual(
            gegevensuitvraagtaak.details["uitvraagLink"], "http://example-new-url.com/"
        )

    def test_destroy(self):
        gegevensuitvraagtaak = ExterneTaakFactory.create(gegevensuitvraagtaak=True)

        detail_url = reverse(
            "taken:gegevensuitvraagtaak-detail",
            kwargs={"uuid": str(gegevensuitvraagtaak.uuid)},
        )

        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(ExterneTaak.objects.exists())


class GegevensuitvraagTaakValidationTests(APITestCase):
    list_url = reverse("taken:gegevensuitvraagtaak-list")

    def test_invalid_create_pass_soort_taak(self):
        self.assertFalse(ExterneTaak.objects.exists())
        # wrong soort_taak
        data = {
            "titel": "titel",
            "handelingsPerspectief": "handelingsPerspectief1",
            "taakSoort": SoortTaak.FORMULIERTAAK.value,
            "details": {
                "uitvraagLink": "http://example.com/",
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
        data["taak_soort"] = SoortTaak.BETAALTAAK.value
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

    def test_invalid_create_type_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
        with self.subTest("invalid start_date gt end_date"):
            data = {
                "titel": "test",
                "handelingsPerspectief": "test",
                "startdatum": datetime.datetime(2025, 1, 1, 10, 0, 0),  # end < start
                "einddatumHandelingsTermijn": datetime.datetime(2024, 1, 1, 10, 0, 0),
                "details": {
                    "uitvraagLink": "http://example.com/",
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
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("invalid url"):
            data = {
                "titel": "titel",
                "handelingsPerspectief": "handelingsPerspectief1",
                "details": {
                    "uitvraagLink": "test",
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.uitvraagLink"),
                {
                    "name": "details.uitvraagLink",
                    "code": "invalid",
                    "reason": "Voer een geldige URL in.",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("invalid none url"):
            data = {
                "titel": "titel",
                "handelingsPerspectief": "handelingsPerspectief1",
                "details": {
                    "uitvraagLink": None,
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.uitvraagLink"),
                {
                    "name": "details.uitvraagLink",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("null value ontvangenGegevens"):
            data = {
                "titel": "titel",
                "handelingsPerspectief": "handelingsPerspectief1",
                "details": {
                    "uitvraagLink": "http://example.com/",
                    "ontvangenGegevens": None,
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.ontvangenGegevens"),
                {
                    "name": "details.ontvangenGegevens",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

    def test_invalid_update_partial(self):
        gegevensuitvraagtaak = ExterneTaakFactory.create(gegevensuitvraagtaak=True)

        detail_url = reverse(
            "taken:gegevensuitvraagtaak-detail",
            kwargs={"uuid": str(gegevensuitvraagtaak.uuid)},
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
