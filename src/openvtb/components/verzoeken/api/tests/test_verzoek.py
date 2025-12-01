import json
from decimal import Decimal

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.verzoeken.models import Verzoek, VerzoekType
from openvtb.components.verzoeken.tests.factories import (
    VerzoekFactory,
    VerzoekTypeFactory,
)
from openvtb.utils.api_testcase import APITestCase


class VerzoekTests(APITestCase):
    list_url = reverse("verzoeken:verzoek-list")
    maxDiff = None

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertEqual(VerzoekType.objects.all().count(), 0)

        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(VerzoekType.objects.all().count(), 1)
        verzoektype = VerzoekType.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('verzoeken:verzoek-detail', kwargs={'uuid': str(verzoek.uuid)})}",
                        "uuid": str(verzoek.uuid),
                        "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                        "geometrie": None,
                        "aanvraagGegevens": verzoek.aanvraag_gegevens,
                        "bijlagen": [],
                        "verzoekBron": {
                            "naam": verzoek.bron.naam,
                            "kenmerk": verzoek.bron.kenmerk,
                        },
                        "verzoekBetaling": {
                            "kenmerken": verzoek.betaling.kenmerken,
                            "bedrag": str(verzoek.betaling.bedrag),
                            "voltooid": verzoek.betaling.voltooid,
                            "transactieDatum": verzoek.betaling.transactie_datum.isoformat().replace(
                                "+00:00", "Z"
                            ),
                            "transactieReferentie": verzoek.betaling.transactie_referentie,
                        },
                    },
                ],
            },
        )

        VerzoekFactory.create(verzoek_type=verzoektype)
        VerzoekFactory.create(verzoek_type=verzoektype)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertEqual(Verzoek.objects.all().count(), 3)

    def test_detail(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoektype = VerzoekType.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('verzoeken:verzoek-detail', kwargs={'uuid': str(verzoek.uuid)})}",
                "uuid": str(verzoek.uuid),
                "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "geometrie": None,
                "aanvraagGegevens": verzoek.aanvraag_gegevens,
                "bijlagen": [],
                "verzoekBron": {
                    "naam": verzoek.bron.naam,
                    "kenmerk": verzoek.bron.kenmerk,
                },
                "verzoekBetaling": {
                    "kenmerken": verzoek.betaling.kenmerken,
                    "bedrag": str(verzoek.betaling.bedrag),
                    "voltooid": verzoek.betaling.voltooid,
                    "transactieDatum": verzoek.betaling.transactie_datum.isoformat().replace(
                        "+00:00", "Z"
                    ),
                    "transactieReferentie": verzoek.betaling.transactie_referentie,
                },
            },
        )

    def test_valid_create(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        data = {
            "geometrie": {"type": "Point", "coordinates": [0, 0]},
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 10,
            },
            "bijlagen": ["string"],
            "verzoekBron": {
                "naam": "string",
                "kenmerk": "string",
            },
            "verzoekBetaling": {
                "kenmerken": ["string"],
                "bedrag": "10",
                "voltooid": True,
                "transactieDatum": "2025-01-01T14:15:22Z",
                "transactieReferentie": "string",
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('verzoeken:verzoek-detail', kwargs={'uuid': str(verzoek.uuid)})}",
                "uuid": str(verzoek.uuid),
                "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoek.verzoek_type.uuid)})}",
                "geometrie": json.loads(verzoek.geometrie.geojson),
                "aanvraagGegevens": verzoek.aanvraag_gegevens,
                "bijlagen": verzoek.bijlagen,
                "verzoekBron": {
                    "naam": verzoek.bron.naam,
                    "kenmerk": verzoek.bron.kenmerk,
                },
                "verzoekBetaling": {
                    "kenmerken": verzoek.betaling.kenmerken,
                    "bedrag": str(verzoek.betaling.bedrag),
                    "voltooid": verzoek.betaling.voltooid,
                    "transactieDatum": verzoek.betaling.transactie_datum.isoformat().replace(
                        "+00:00", "Z"
                    ),
                    "transactieReferentie": verzoek.betaling.transactie_referentie,
                },
            },
        )

    def test_invalid_create_required(self):
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 2)
        self.assertEqual(
            get_validation_errors(response, "verzoekType"),
            {
                "name": "verzoekType",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "aanvraagGegevens"),
            {
                "name": "aanvraagGegevens",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(VerzoekType.objects.all().count(), 0)

    def test_valid_update_partial(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        # empty PATCH
        data = {}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # aanvraagGegevens PATCH
        self.assertEqual(verzoek.aanvraag_gegevens["diameter"], 10)
        data = {
            "aanvraagGegevens": {
                "diameter": 20,
            },
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.aanvraag_gegevens["diameter"], 20)

        # verzoekBron and verzoekBetaling PATCH
        data = {
            "verzoekBron": {
                "naam": "new_naam",
            },
            "verzoekBetaling": {
                "bedrag": "55",
            },
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bron.naam, "new_naam")
        self.assertEqual(verzoek.betaling.bedrag, Decimal(55))

    def test_valid_update(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )
        data = {
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 20,
            },
            "verzoekBron": {
                "naam": "new_naam",
                "kenmerk": "new_kenmerk",
            },
            "verzoekBetaling": {
                "bedrag": "10",
                "transactieReferentie": "new_ref",
            },
        }
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bron.naam, "new_naam")
        self.assertEqual(verzoek.bron.kenmerk, "new_kenmerk")
        self.assertEqual(verzoek.betaling.bedrag, Decimal(10))
        self.assertEqual(verzoek.betaling.transactie_referentie, "new_ref")
        self.assertEqual(verzoek.aanvraag_gegevens["diameter"], 20)

    def test_invalid_update_required(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )
        data = {}
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 2)
        self.assertEqual(
            get_validation_errors(response, "verzoekType"),
            {
                "name": "verzoekType",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "aanvraagGegevens"),
            {
                "name": "aanvraagGegevens",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_update_partial_bron_betaling(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        # verzoekBron and verzoekBetaling are None
        self.assertFalse(hasattr(verzoek, "bron"))
        self.assertFalse(hasattr(verzoek, "betaling"))

        data = {
            "verzoekBron": {
                "naam": "new_naam",
            },
            "verzoekBetaling": {
                "bedrag": "55",
            },
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bron.naam, "new_naam")
        self.assertEqual(verzoek.betaling.bedrag, Decimal(55))

    def test_destroy(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        self.assertEqual(Verzoek.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertEqual(Verzoek.objects.all().count(), 0)
