import datetime

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.berichten.models import Bericht
from openvtb.components.berichten.tests.factories import (
    BerichtFactory,
    BerichtOntvangerFactory,
)
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-01-01")
class BerichtTests(APITestCase):
    list_url = reverse("berichten:bericht-list")
    maxDiff = None

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(Bericht.objects.exists())

        # create bericht
        BerichtFactory.create(create_bijlage=True)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(Bericht.objects.all().count(), 1)

        bericht = Bericht.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('berichten:bericht-detail', kwargs={'uuid': str(bericht.uuid)})}",
                        "urn": f"urn:maykin:berichten:bericht:{str(bericht.uuid)}",
                        "uuid": str(bericht.uuid),
                        "onderwerp": bericht.onderwerp,
                        "berichtTekst": bericht.bericht_tekst,
                        "publicatiedatum": bericht.publicatiedatum.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "referentie": bericht.referentie,
                        "ontvanger": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(bericht.ontvanger.uuid)})}",
                        "ontvangerUrn": f"urn:maykin:berichten:berichtontvanger:{str(bericht.ontvanger.uuid)}",
                        "berichtType": bericht.bericht_type,
                        "handelingsPerspectief": bericht.handelings_perspectief,
                        "einddatumHandelingsTermijn": bericht.einddatum_handelings_termijn.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "bijlagen": [
                            {
                                "informatieObject": bericht.bijlagen.first().informatie_object,
                                "omschrijving": bericht.bijlagen.first().omschrijving,
                            },
                        ],
                    },
                ],
            },
        )

        BerichtFactory.create()
        BerichtFactory.create()
        BerichtFactory.create()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 4)
        self.assertEqual(Bericht.objects.all().count(), 4)

    def test_list_pagination_pagesize_param(self):
        BerichtFactory.create_batch(10)
        response = self.client.get(self.list_url, {"pageSize": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(response.json()["count"], 10)
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertEqual(
            data["next"], f"http://testserver{self.list_url}?page=2&pageSize=5"
        )

    def test_detail(self):
        bericht = BerichtFactory.create(create_bijlage=True)
        detail_url = reverse(
            "berichten:bericht-detail", kwargs={"uuid": str(bericht.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:bericht-detail', kwargs={'uuid': str(bericht.uuid)})}",
                "urn": f"urn:maykin:berichten:bericht:{str(bericht.uuid)}",
                "uuid": str(bericht.uuid),
                "onderwerp": bericht.onderwerp,
                "berichtTekst": bericht.bericht_tekst,
                "publicatiedatum": bericht.publicatiedatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "referentie": bericht.referentie,
                "ontvanger": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(bericht.ontvanger.uuid)})}",
                "ontvangerUrn": f"urn:maykin:berichten:berichtontvanger:{str(bericht.ontvanger.uuid)}",
                "berichtType": bericht.bericht_type,
                "handelingsPerspectief": bericht.handelings_perspectief,
                "einddatumHandelingsTermijn": bericht.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "bijlagen": [
                    {
                        "informatieObject": bericht.bijlagen.first().informatie_object,
                        "omschrijving": bericht.bijlagen.first().omschrijving,
                    },
                ],
            },
        )

    def test_valid_create(self):
        self.assertFalse(Bericht.objects.exists())
        ontvanger = BerichtOntvangerFactory.create()
        data = {
            "onderwerp": "onderwerp",
            "berichtTekst": "berichtTekst berichtTekst",
            "publicatiedatum": datetime.datetime.now(),
            "referentie": "referentie",
            "ontvanger": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
            "berichtType": "12345678",
            "handelingsPerspectief": "test",
            "einddatumHandelingsTermijn": datetime.datetime.now(),
            "bijlagen": [
                {
                    "informatieObject": "urn:maykin:test1",
                    "omschrijving": "test1",
                },
                {
                    "informatieObject": "urn:maykin:test2",
                    "omschrijving": "test2",
                },
            ],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bericht.objects.all().count(), 1)

        bericht = Bericht.objects.get()
        bijlage1 = bericht.bijlagen.get(informatie_object="urn:maykin:test1")
        bijlage2 = bericht.bijlagen.get(informatie_object="urn:maykin:test2")

        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:bericht-detail', kwargs={'uuid': str(bericht.uuid)})}",
                "urn": f"urn:maykin:berichten:bericht:{str(bericht.uuid)}",
                "uuid": str(bericht.uuid),
                "onderwerp": bericht.onderwerp,
                "berichtTekst": bericht.bericht_tekst,
                "publicatiedatum": bericht.publicatiedatum.isoformat().replace(
                    "+00:00", "Z"
                ),
                "referentie": bericht.referentie,
                "ontvanger": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(bericht.ontvanger.uuid)})}",
                "ontvangerUrn": f"urn:maykin:berichten:berichtontvanger:{str(bericht.ontvanger.uuid)}",
                "berichtType": bericht.bericht_type,
                "handelingsPerspectief": bericht.handelings_perspectief,
                "einddatumHandelingsTermijn": bericht.einddatum_handelings_termijn.isoformat().replace(
                    "+00:00", "Z"
                ),
                "bijlagen": [
                    {
                        "informatieObject": bijlage1.informatie_object,
                        "omschrijving": bijlage1.omschrijving,
                    },
                    {
                        "informatieObject": bijlage2.informatie_object,
                        "omschrijving": bijlage2.omschrijving,
                    },
                ],
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertFalse(Bericht.objects.exists())
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 3)
        self.assertEqual(
            get_validation_errors(response, "onderwerp"),
            {
                "name": "onderwerp",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "berichtTekst"),
            {
                "name": "berichtTekst",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "ontvanger"),
            {
                "name": "ontvanger",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_update_not_allowed(self):
        bericht = BerichtFactory.create(create_bijlage=True)
        detail_url = reverse(
            "berichten:bericht-detail", kwargs={"uuid": str(bericht.uuid)}
        )

        # PATCH
        data = {}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["code"], "method_not_allowed")
        self.assertEqual(response.data["detail"], 'Methode "PATCH" niet toegestaan.')

        # PUT
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["code"], "method_not_allowed")
        self.assertEqual(response.data["detail"], 'Methode "PUT" niet toegestaan.')

    def test_destroy_not_allowed(self):
        bericht = BerichtFactory.create(create_bijlage=True)
        detail_url = reverse(
            "berichten:bericht-detail", kwargs={"uuid": str(bericht.uuid)}
        )

        # DELETE
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["code"], "method_not_allowed")
        self.assertEqual(response.data["detail"], 'Methode "DELETE" niet toegestaan.')
