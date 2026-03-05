import json
from decimal import Decimal

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.verzoeken.models import Bijlage, Verzoek, VerzoekType
from openvtb.components.verzoeken.tests.factories import (
    VerzoekFactory,
    VerzoekTypeFactory,
    VerzoekTypeVersionFactory,
)
from openvtb.utils.api_testcase import APITestCase


class VerzoekTests(APITestCase):
    list_url = reverse("verzoeken:verzoek-list")
    maxDiff = None

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(VerzoekType.objects.exists())

        verzoektype = VerzoekTypeFactory.create(create_versie=True)
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
                        "urn": f"urn:maykin:verzoeken:verzoek:{str(verzoek.uuid)}",
                        "uuid": str(verzoek.uuid),
                        "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                        "verzoekTypeUrn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                        "geometrie": None,
                        "versie": 1,
                        "aanvraagGegevens": verzoek.aanvraag_gegevens,
                        "bijlagen": [],
                        "isGerelateerdAan": [],
                        "kanaal": "",
                        "verzoekInformatieObject": "",
                        "verzoekTaal": "nld",
                        "initiator": verzoek.initiator,
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
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
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
                "urn": f"urn:maykin:verzoeken:verzoek:{str(verzoek.uuid)}",
                "uuid": str(verzoek.uuid),
                "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "verzoekTypeUrn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                "geometrie": None,
                "aanvraagGegevens": verzoek.aanvraag_gegevens,
                "versie": 1,
                "bijlagen": [],
                "initiator": verzoek.initiator,
                "isGerelateerdAan": verzoek.is_gerelateerd_aan,
                "kanaal": verzoek.kanaal,
                "verzoekInformatieObject": verzoek.verzoek_informatie_object,
                "verzoekTaal": "nld",
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
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        data = {
            "geometrie": {"type": "Point", "coordinates": [0, 0]},
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 10,
            },
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                },
            ],
            "verzoekBron": {
                "naam": "string",
                "kenmerk": "string",
            },
            "kanaal": "test",
            "verzoekInformatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
            "verzoekBetaling": {
                "kenmerken": ["string"],
                "bedrag": "10",
                "voltooid": True,
                "transactieDatum": "2026-01-01T14:15:22Z",
                "transactieReferentie": "string",
            },
            "initiator": "urn:nld:brp:bsn:111222333",
            "isGerelateerdAan": [
                {"urn": "urn:nld:gemeenteutrecht:zaak:zaaknummer:00011111"},
                {"urn": "urn:nld:gemeenteutrecht:zaak:zaaknummer:00022222"},
            ],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('verzoeken:verzoek-detail', kwargs={'uuid': str(verzoek.uuid)})}",
                "urn": f"urn:maykin:verzoeken:verzoek:{str(verzoek.uuid)}",
                "uuid": str(verzoek.uuid),
                "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoek.verzoek_type.uuid)})}",
                "verzoekTypeUrn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                "geometrie": json.loads(verzoek.geometrie.geojson),
                "aanvraagGegevens": verzoek.aanvraag_gegevens,
                "versie": 1,
                "bijlagen": [
                    {
                        "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                    }
                ],
                "initiator": verzoek.initiator,
                "isGerelateerdAan": verzoek.is_gerelateerd_aan,
                "kanaal": verzoek.kanaal,
                "verzoekInformatieObject": verzoek.verzoek_informatie_object,
                "verzoekTaal": verzoek.verzoek_taal,
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

    def test_valid_create_with_external_relations(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        data = {
            "geometrie": {"type": "Point", "coordinates": [0, 0]},
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 10,
            },
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                },
            ],
            "isGerelateerdAan": [
                {"urn": "urn:nld:gemeenteutrecht:zaak:zaaknummer:00011111"},
                {"urn": "urn:nld:gemeenteutrecht:zaak:zaaknummer:00022222"},
            ],
            "verzoekBron": {
                "naam": "string",
                "kenmerk": "string",
            },
            "verzoekBetaling": {
                "kenmerken": ["string"],
                "bedrag": "10",
                "voltooid": True,
                "transactieDatum": "2026-01-01T14:15:22Z",
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
                "urn": f"urn:maykin:verzoeken:verzoek:{str(verzoek.uuid)}",
                "uuid": str(verzoek.uuid),
                "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoek.verzoek_type.uuid)})}",
                "verzoekTypeUrn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                "geometrie": json.loads(verzoek.geometrie.geojson),
                "aanvraagGegevens": verzoek.aanvraag_gegevens,
                "versie": 1,
                "bijlagen": [
                    {
                        "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                    }
                ],
                "initiator": verzoek.initiator,
                "isGerelateerdAan": verzoek.is_gerelateerd_aan,
                "kanaal": verzoek.kanaal,
                "verzoekInformatieObject": verzoek.verzoek_informatie_object,
                "verzoekTaal": verzoek.verzoek_taal,
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

    def test_create_bijlagen(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        data = {
            "geometrie": {"type": "Point", "coordinates": [0, 0]},
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 10,
            },
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                },
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:7bf3ab4a-3458-400f-80ad-8a2c85b12a8d",
                },
            ],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoek = Verzoek.objects.get()

        self.assertEqual(verzoek.bijlagen.count(), 2)

    def test_invalid_create_required(self):
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
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
        self.assertFalse(VerzoekType.objects.exists())

    def test_create_with_empty_versie(self):
        # if versie not provide should take the last_versie.versie
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        last_versie = VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)

        self.assertEqual(verzoektype.versies.count(), 2)
        self.assertEqual(verzoektype.last_versie, last_versie)
        self.assertEqual(verzoektype.last_versie.versie, 2)  # second versie

        data = {
            "geometrie": {"type": "Point", "coordinates": [0, 0]},
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {"diameter": 10},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        verzoek = Verzoek.objects.get()
        self.assertEqual(verzoek.versie, 2)  # last_versie.versie

    def test_valid_update_partial(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
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
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
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
            "versie": 2,
            "verzoekBron": {
                "naam": "new_naam",
                "kenmerk": "new_kenmerk",
            },
            "verzoekBetaling": {
                "bedrag": "10",
                "transactieReferentie": "new_ref",
            },
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                },
            ],
            "initiator": "urn:example:12345",
            "verzoekTaal": "eng",
        }
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bron.naam, "new_naam")
        self.assertEqual(verzoek.bron.kenmerk, "new_kenmerk")
        self.assertEqual(verzoek.betaling.bedrag, Decimal(10))
        self.assertEqual(verzoek.betaling.transactie_referentie, "new_ref")
        self.assertEqual(verzoek.aanvraag_gegevens["diameter"], 20)
        self.assertEqual(verzoek.versie, 2)
        self.assertEqual(
            verzoek.bijlagen.first().informatie_object,
            "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
        )
        self.assertEqual(verzoek.initiator, "urn:example:12345")
        self.assertEqual(verzoek.verzoek_taal, "eng")

    def test_update_with_bijlagen(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )
        Bijlage.objects.create(
            verzoek=verzoek,
            informatie_object="urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
        )
        Bijlage.objects.create(
            verzoek=verzoek,
            informatie_object="urn:nld:gemeenteutrecht:informatieobject:uuid:2f985cf7-e9f0-45fb-8c52-05688e06705d",
        )

        # create in this case, because doesn't exist with this informatie_object
        data = {
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:32af74f4-a7a2-4414-a9de-b50e35325cc6",
                },
            ],
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bijlagen.count(), 3)

    def test_invalid_update_required(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )
        data = {}
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
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
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
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
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )

        self.assertEqual(Verzoek.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(Verzoek.objects.exists())
