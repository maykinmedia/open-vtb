import datetime
import uuid

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-01-01")
class URLTaakTests(APITestCase):
    list_url = reverse("taken:urltaak-list")

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(ExterneTaak.objects.exists())

        # create 1 urltaak
        ExterneTaakFactory.create(urltaak=True)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        urltaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(urltaak.uuid)})}",
                        "urn": f"urn:maykin:taken:externetaak:{str(urltaak.uuid)}",
                        "uuid": str(urltaak.uuid),
                        "titel": urltaak.titel,
                        "status": urltaak.status,
                        "verwerkerTaakId": urltaak.verwerker_taak_id,
                        "startdatum": urltaak.startdatum.isoformat(),
                        "handelingsPerspectief": urltaak.handelings_perspectief,
                        "einddatumHandelingsTermijn": urltaak.einddatum_handelings_termijn.isoformat(),
                        "datumHerinnering": urltaak.datum_herinnering.isoformat(),
                        "toelichting": urltaak.toelichting,
                        "isToegewezenAan": urltaak.is_toegewezen_aan,
                        "isGerelateerdAan": urltaak.is_gerelateerd_aan,
                        "taakSoort": urltaak.taak_soort,
                        "details": {
                            "uitvraagLink": urltaak.details["uitvraagLink"],
                            "voorinvullenGegevens": urltaak.details[
                                "voorinvullenGegevens"
                            ],
                            "ontvangenGegevens": urltaak.details["ontvangenGegevens"],
                        },
                    },
                ],
            },
        )

        # create 1 betaaltaak
        ExterneTaakFactory.create(betaaltaak=True)

        # assert only 1 urltaak
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(
            response.json()["results"][0]["uuid"],
            str(urltaak.uuid),
        )

        # assert 2 total externeTaak
        self.assertEqual(ExterneTaak.objects.all().count(), 2)

    def test_detail(self):
        urltaak = ExterneTaakFactory.create(urltaak=True)
        detail_url = reverse(
            "taken:urltaak-detail",
            kwargs={"uuid": str(urltaak.uuid)},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(urltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(urltaak.uuid)}",
                "uuid": str(urltaak.uuid),
                "titel": urltaak.titel,
                "status": urltaak.status,
                "verwerkerTaakId": urltaak.verwerker_taak_id,
                "startdatum": urltaak.startdatum.isoformat(),
                "handelingsPerspectief": urltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": urltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": urltaak.datum_herinnering.isoformat(),
                "toelichting": urltaak.toelichting,
                "isToegewezenAan": urltaak.is_toegewezen_aan,
                "isGerelateerdAan": urltaak.is_gerelateerd_aan,
                "taakSoort": urltaak.taak_soort,
                "details": {
                    "uitvraagLink": urltaak.details["uitvraagLink"],
                    "voorinvullenGegevens": urltaak.details["voorinvullenGegevens"],
                    "ontvangenGegevens": urltaak.details["ontvangenGegevens"],
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
            "taken:urltaak-detail",
            kwargs={"uuid": str(betaaltaak.uuid)},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_create(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "uitvraagLink": "http://example.com/",
                "voorinvullenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                    },
                },
                "ontvangenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                    },
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
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(urltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(urltaak.uuid)}",
                "uuid": str(urltaak.uuid),
                "titel": urltaak.titel,
                "status": urltaak.status,
                "verwerkerTaakId": urltaak.verwerker_taak_id,
                "startdatum": urltaak.startdatum.isoformat(),
                "handelingsPerspectief": urltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": urltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": urltaak.datum_herinnering.isoformat(),
                "toelichting": urltaak.toelichting,
                "isToegewezenAan": urltaak.is_toegewezen_aan,
                "isGerelateerdAan": urltaak.is_gerelateerd_aan,
                "taakSoort": urltaak.taak_soort,
                "details": {
                    "uitvraagLink": urltaak.details["uitvraagLink"],
                    "voorinvullenGegevens": urltaak.details["voorinvullenGegevens"],
                    "ontvangenGegevens": urltaak.details["ontvangenGegevens"],
                },
            },
        )

        # no ontvangenGegevens key
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "uitvraagLink": "http://example.com/",
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 2)
        urltaak = ExterneTaak.objects.get(uuid=response.json()["uuid"])
        self.assertEqual(urltaak.details["ontvangenGegevens"], {})

        # empty value ontvangenGegevens
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "uitvraagLink": "http://example.com/",
                "voorinvullenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                    },
                },
                "ontvangenGegevens": {},
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 3)
        urltaak = ExterneTaak.objects.get(uuid=response.json()["uuid"])
        self.assertEqual(urltaak.details["ontvangenGegevens"], {})

        # test datumHerinnering auto filled
        # einddatumHandelingsTermijn - TAKEN_DEFAULT_REMINDER_IN_DAYS(7 days)
        self.assertEqual(urltaak.datum_herinnering, datetime.date(2026, 1, 3))

    def test_valid_create_with_external_relations(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "uitvraagLink": "http://example.com/",
                "voorinvullenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                    },
                },
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
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(urltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(urltaak.uuid)}",
                "uuid": str(urltaak.uuid),
                "titel": urltaak.titel,
                "status": urltaak.status,
                "verwerkerTaakId": urltaak.verwerker_taak_id,
                "startdatum": urltaak.startdatum.isoformat(),
                "handelingsPerspectief": urltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": urltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": urltaak.datum_herinnering.isoformat(),
                "toelichting": urltaak.toelichting,
                "isToegewezenAan": urltaak.is_toegewezen_aan,
                "isGerelateerdAan": urltaak.is_gerelateerd_aan,
                "taakSoort": urltaak.taak_soort,
                "details": {
                    "uitvraagLink": urltaak.details["uitvraagLink"],
                    "voorinvullenGegevens": urltaak.details["voorinvullenGegevens"],
                    "ontvangenGegevens": urltaak.details["ontvangenGegevens"],
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

        # empty details values
        data = {
            "titel": "test",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
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
        urltaak = ExterneTaakFactory.create(urltaak=True)

        detail_url = reverse(
            "taken:urltaak-detail",
            kwargs={"uuid": str(urltaak.uuid)},
        )
        # empty PATCH
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(urltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(urltaak.uuid)}",
                "uuid": str(urltaak.uuid),
                "titel": urltaak.titel,
                "status": urltaak.status,
                "verwerkerTaakId": urltaak.verwerker_taak_id,
                "startdatum": urltaak.startdatum.isoformat(),
                "handelingsPerspectief": urltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": urltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": urltaak.datum_herinnering.isoformat(),
                "toelichting": urltaak.toelichting,
                "isToegewezenAan": urltaak.is_toegewezen_aan,
                "isGerelateerdAan": urltaak.is_gerelateerd_aan,
                "taakSoort": urltaak.taak_soort,
                "details": {
                    "uitvraagLink": urltaak.details["uitvraagLink"],
                    "voorinvullenGegevens": urltaak.details["voorinvullenGegevens"],
                    "ontvangenGegevens": urltaak.details["ontvangenGegevens"],
                },
            },
        )

        # patch externe_taak field
        response = self.client.patch(detail_url, {"titel": "new_title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(urltaak.titel, "new_title")

        # patch one field from json_data
        self.assertEqual(
            urltaak.details["uitvraagLink"], "http://example.com/"
        )  # default factory value
        response = self.client.patch(
            detail_url, {"details": {"uitvraagLink": "http://example-new-url.com/"}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(urltaak.details["uitvraagLink"], "http://example-new-url.com/")

        # update ontvangenGegevens
        self.assertEqual(
            urltaak.details["ontvangenGegevens"], {"key": "value"}
        )  # default
        response = self.client.patch(
            detail_url, {"details": {"ontvangenGegevens": {"new_key": "new_value"}}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urltaak = ExterneTaak.objects.get()
        # new value
        self.assertEqual(urltaak.details["ontvangenGegevens"], {"new_key": "new_value"})
        self.assertNotEqual(urltaak.details["ontvangenGegevens"], {"key": "value"})

        # update voorinvullenGegevens
        self.assertEqual(
            urltaak.details["voorinvullenGegevens"], {"key": "value"}
        )  # default
        response = self.client.patch(
            detail_url, {"details": {"voorinvullenGegevens": {"new_key": "new_value"}}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urltaak = ExterneTaak.objects.get()

        # new value
        self.assertEqual(
            urltaak.details["voorinvullenGegevens"],
            {"new_key": "new_value"},
        )
        self.assertNotEqual(urltaak.details["voorinvullenGegevens"], {"key": "value"})

        # patch isToegewezenAan with the new details
        response = self.client.patch(
            detail_url, {"isToegewezenAan": "urn:example:12345"}
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

    def test_valid_update(self):
        urltaak = ExterneTaakFactory.create(urltaak=True)

        detail_url = reverse(
            "taken:urltaak-detail",
            kwargs={"uuid": str(urltaak.uuid)},
        )

        # all required PUT fields
        response = self.client.put(
            detail_url,
            {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "uitvraagLink": "http://example-new-url.com/",
                },
            },
        )
        urltaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(urltaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(urltaak.uuid)}",
                "uuid": str(urltaak.uuid),
                "titel": urltaak.titel,
                "status": urltaak.status,
                "verwerkerTaakId": urltaak.verwerker_taak_id,
                "startdatum": urltaak.startdatum.isoformat(),
                "handelingsPerspectief": urltaak.handelings_perspectief,
                "einddatumHandelingsTermijn": urltaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": urltaak.datum_herinnering.isoformat(),
                "toelichting": urltaak.toelichting,
                "isToegewezenAan": urltaak.is_toegewezen_aan,
                "isGerelateerdAan": urltaak.is_gerelateerd_aan,
                "taakSoort": urltaak.taak_soort,
                "details": {
                    "uitvraagLink": urltaak.details["uitvraagLink"],
                    "voorinvullenGegevens": urltaak.details["voorinvullenGegevens"],
                    "ontvangenGegevens": urltaak.details["ontvangenGegevens"],
                },
            },
        )
        self.assertEqual(urltaak.details["uitvraagLink"], "http://example-new-url.com/")

    def test_destroy(self):
        urltaak = ExterneTaakFactory.create(urltaak=True)

        detail_url = reverse(
            "taken:urltaak-detail",
            kwargs={"uuid": str(urltaak.uuid)},
        )

        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(ExterneTaak.objects.exists())


class urltaakValidationTests(APITestCase):
    list_url = reverse("taken:urltaak-list")

    def test_invalid_create_pass_soort_taak(self):
        self.assertFalse(ExterneTaak.objects.exists())
        # wrong soort_taak
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": SoortTaak.FORMULIERTAAK.value,
            "details": {
                "uitvraagLink": "http://example.com/",
            },
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
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
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
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
                "startdatum": datetime.date(2026, 1, 10),  # end < start
                "einddatumHandelingsTermijn": datetime.date(2025, 1, 10),
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
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
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
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
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
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
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
        urltaak = ExterneTaakFactory.create(urltaak=True)

        detail_url = reverse(
            "taken:urltaak-detail",
            kwargs={"uuid": str(urltaak.uuid)},
        )
        # pass taak_soort
        response = self.client.patch(
            detail_url, {"taakSoort": SoortTaak.FORMULIERTAAK.value}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )
