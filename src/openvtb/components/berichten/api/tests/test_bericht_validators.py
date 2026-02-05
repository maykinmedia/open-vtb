import uuid

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.berichten.models import Bericht
from openvtb.components.berichten.tests.factories import (
    BerichtOntvangerFactory,
)
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-01-01")
class BerichtValidatorsTests(APITestCase):
    list_url = reverse("berichten:bericht-list")
    maxDiff = None

    def test_invalid_ontvanger_create(self):
        with self.subTest("invalid ontvanger url"):
            data = {
                "onderwerp": "onderwerp",
                "berichtTekst": "berichtTekst berichtTekst",
                "ontvanger": "test",  # invalid url
            }
            response = self.client.post(self.list_url, data)
            self.assertFalse(Bericht.objects.exists())

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["code"], "invalid")
            self.assertEqual(response.data["title"], "Invalid input.")
            self.assertEqual(len(response.data["invalid_params"]), 1)
            self.assertEqual(
                get_validation_errors(response, "ontvanger"),
                {
                    "name": "ontvanger",
                    "code": "no_match",
                    "reason": "Ongeldige hyperlink - Geen overeenkomende URL.",
                },
            )
            data = {
                "onderwerp": "onderwerp",
                "berichtTekst": "berichtTekst berichtTekst",
                "ontvanger": "http://testserver.test",
            }
            response = self.client.post(self.list_url, data)
            self.assertFalse(Bericht.objects.exists())

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["code"], "invalid")
            self.assertEqual(response.data["title"], "Invalid input.")
            self.assertEqual(len(response.data["invalid_params"]), 1)
            self.assertEqual(
                get_validation_errors(response, "ontvanger"),
                {
                    "name": "ontvanger",
                    "code": "no_match",
                    "reason": "Ongeldige hyperlink - Geen overeenkomende URL.",
                },
            )

        with self.subTest("does not exists random ontvanger"):
            data = {
                "onderwerp": "onderwerp",
                "berichtTekst": "berichtTekst berichtTekst",
                "ontvanger": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(uuid.uuid4())})}",
            }
            response = self.client.post(self.list_url, data)
            self.assertFalse(Bericht.objects.exists())

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["code"], "invalid")
            self.assertEqual(response.data["title"], "Invalid input.")
            self.assertEqual(len(response.data["invalid_params"]), 1)
            self.assertEqual(
                get_validation_errors(response, "ontvanger"),
                {
                    "name": "ontvanger",
                    "code": "does_not_exist",
                    "reason": "Ongeldige hyperlink - Object bestaat niet.",
                },
            )

        with self.subTest("ontvanger required"):
            data = {
                "onderwerp": "onderwerp",
                "berichtTekst": "berichtTekst berichtTekst",
            }
            response = self.client.post(self.list_url, data)
            self.assertFalse(Bericht.objects.exists())

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["code"], "invalid")
            self.assertEqual(response.data["title"], "Invalid input.")
            self.assertEqual(len(response.data["invalid_params"]), 1)
            self.assertEqual(
                get_validation_errors(response, "ontvanger"),
                {
                    "name": "ontvanger",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
            )

    def test_invalid_bilaje_create(self):
        self.assertFalse(Bericht.objects.exists())
        ontvanger = BerichtOntvangerFactory.create()

        with self.subTest("informatieObject required"):
            data = {
                "onderwerp": "onderwerp",
                "berichtTekst": "berichtTekst berichtTekst",
                "ontvanger": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
                "bijlagen": [
                    {
                        "omschrijving": "test1",
                    }
                ],
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["code"], "invalid")
            self.assertEqual(response.data["title"], "Invalid input.")
            self.assertEqual(len(response.data["invalid_params"]), 1)
            self.assertEqual(
                get_validation_errors(response, "bijlagen.0.informatieObject"),
                {
                    "name": "bijlagen.0.informatieObject",
                    "code": "required",
                    "reason": "Dit veld is vereist.",
                },
            )

        with self.subTest("informatieObject duplicated"):
            data = {
                "onderwerp": "onderwerp",
                "berichtTekst": "berichtTekst berichtTekst",
                "ontvanger": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
                "bijlagen": [
                    {
                        "informatieObject": "urn:maykin:test1",
                        "omschrijving": "test1",
                    },
                    {
                        "informatieObject": "urn:maykin:test1",
                        "omschrijving": "test1",
                    },
                ],
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["code"], "invalid")
            self.assertEqual(response.data["title"], "Invalid input.")
            self.assertEqual(len(response.data["invalid_params"]), 1)
            self.assertEqual(
                get_validation_errors(response, "bijlagen"),
                {
                    "name": "bijlagen",
                    "code": "unique",
                    "reason": "Bijlage with the specified informatieObject already exists.",
                },
            )
