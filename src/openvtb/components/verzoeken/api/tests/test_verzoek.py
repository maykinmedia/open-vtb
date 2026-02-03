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

        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(
            create_details=True,
            verzoek_type=verzoektype,
            niet_authentieke_persoonsgegevens=True,
        )

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
                        "version": 1,
                        "aanvraagGegevens": verzoek.aanvraag_gegevens,
                        "bijlagen": [],
                        "isGerelateerdAan": "",
                        "kanaal": "",
                        "authenticatieContext": "",
                        "informatieObject": "",
                        "isIngediendDoor": {
                            "authentiekeVerwijzing": None,
                            "nietAuthentiekePersoonsgegevens": {
                                "voornaam": "Jan",
                                "achternaam": "Jansen",
                                "geboortedatum": "1980-05-15",
                                "emailadres": "jan.jansen@example.com",
                                "telefoonnummer": "+31612345678",
                                "postadres": {"key": "value"},
                                "verblijfsadres": {"key": "value"},
                            },
                            "nietAuthentiekeOrganisatiegegevens": None,
                        },
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
        verzoek = VerzoekFactory.create(
            create_details=True,
            verzoek_type=verzoektype,
            authentieke_verwijzing=True,
        )
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
                "version": 1,
                "bijlagen": [],
                "isIngediendDoor": {
                    "authentiekeVerwijzing": verzoek.is_ingediend_door[
                        "authentiekeVerwijzing"
                    ],
                    "nietAuthentiekePersoonsgegevens": None,
                    "nietAuthentiekeOrganisatiegegevens": None,
                },
                "isGerelateerdAan": verzoek.is_gerelateerd_aan,
                "kanaal": verzoek.kanaal,
                "authenticatieContext": verzoek.authenticatie_context,
                "informatieObject": verzoek.informatie_object,
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
            "version": 1,
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                    "toelichting": "test1",
                },
            ],
            "verzoekBron": {
                "naam": "string",
                "kenmerk": "string",
            },
            "kanaal": "test",
            "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
            "verzoekBetaling": {
                "kenmerken": ["string"],
                "bedrag": "10",
                "voltooid": True,
                "transactieDatum": "2026-01-01T14:15:22Z",
                "transactieReferentie": "string",
            },
            "isIngediendDoor": {
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": {"key": "value"},
                    "postadres": {
                        "keyCamelCase": "value_test",
                        "key_snake_case": "valueTest",
                    },
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                }
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
                "version": 1,
                "bijlagen": [
                    {
                        "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                        "toelichting": "test1",
                    }
                ],
                "isIngediendDoor": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekePersoonsgegevens": None,
                    "nietAuthentiekeOrganisatiegegevens": {
                        "postadres": {
                            "keyCamelCase": "value_test",
                            "key_snake_case": "valueTest",
                        },
                        "emailadres": "info@acme.nl",
                        "bezoekadres": {"key": "value"},
                        "statutaireNaam": "Acme BV",
                        "telefoonnummer": "+31201234567",
                    },
                },
                "isGerelateerdAan": verzoek.is_gerelateerd_aan,
                "kanaal": verzoek.kanaal,
                "authenticatieContext": verzoek.authenticatie_context,
                "informatieObject": verzoek.informatie_object,
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
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        data = {
            "geometrie": {"type": "Point", "coordinates": [0, 0]},
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 10,
            },
            "version": 1,
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                    "toelichting": "test1",
                },
            ],
            "isIngediendDoor": {},
            "isGerelateerdAan": "urn:maykin:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "authenticatieContext": "",
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
                "version": 1,
                "bijlagen": [
                    {
                        "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                        "toelichting": "test1",
                    }
                ],
                "isIngediendDoor": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekeOrganisatiegegevens": None,
                    "nietAuthentiekePersoonsgegevens": None,
                },
                "isGerelateerdAan": verzoek.is_gerelateerd_aan,
                "kanaal": verzoek.kanaal,
                "authenticatieContext": verzoek.authenticatie_context,
                "informatieObject": verzoek.informatie_object,
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
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        data = {
            "geometrie": {"type": "Point", "coordinates": [0, 0]},
            "verzoekType": reverse(
                "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
            ),
            "aanvraagGegevens": {
                "diameter": 10,
            },
            "version": 1,
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                    "toelichting": "test1",
                },
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:7bf3ab4a-3458-400f-80ad-8a2c85b12a8d",
                    "toelichting": "test2",
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
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 3)
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
        self.assertEqual(
            get_validation_errors(response, "version"),
            {
                "name": "version",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertFalse(VerzoekType.objects.exists())

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
        VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        verzoek = VerzoekFactory.create(
            create_details=True,
            verzoek_type=verzoektype,
            niet_authentieke_persoonsgegevens=True,
        )
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
            "version": 2,
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
                    "toelichting": "test1",
                },
            ],
            "isIngediendDoor": {"authentiekeVerwijzing": {"urn": "urn:example:12345"}},
        }
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bron.naam, "new_naam")
        self.assertEqual(verzoek.bron.kenmerk, "new_kenmerk")
        self.assertEqual(verzoek.betaling.bedrag, Decimal(10))
        self.assertEqual(verzoek.betaling.transactie_referentie, "new_ref")
        self.assertEqual(verzoek.aanvraag_gegevens["diameter"], 20)
        self.assertEqual(verzoek.version, 2)
        self.assertEqual(
            verzoek.bijlagen.first().informatie_object,
            "urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
        )
        self.assertEqual(verzoek.bijlagen.first().toelichting, "test1")
        self.assertEqual(
            verzoek.is_ingediend_door,
            {"authentiekeVerwijzing": {"urn": "urn:example:12345"}},
        )

    def test_update_with_bijlagen(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        verzoek = VerzoekFactory.create(create_details=True, verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )
        Bijlage.objects.create(
            verzoek=verzoek,
            informatie_object="urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
            toelichting="description1",
        )
        Bijlage.objects.create(
            verzoek=verzoek,
            informatie_object="urn:nld:gemeenteutrecht:informatieobject:uuid:2f985cf7-e9f0-45fb-8c52-05688e06705d",
            toelichting="description2",
        )

        # create in this case, because doesn't exist with this informatie_object
        data = {
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:32af74f4-a7a2-4414-a9de-b50e35325cc6",
                    "toelichting": "test3",
                },
            ],
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bijlagen.count(), 3)

        # update in this case, because it exist with this informatie_object
        data = {
            "bijlagen": [
                {
                    "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:32af74f4-a7a2-4414-a9de-b50e35325cc6",
                    "toelichting": "new_test3",
                },
            ],
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek.refresh_from_db()
        self.assertEqual(verzoek.bijlagen.count(), 3)
        self.assertEqual(
            verzoek.bijlagen.get(
                informatie_object="urn:nld:gemeenteutrecht:informatieobject:uuid:32af74f4-a7a2-4414-a9de-b50e35325cc6"
            ).toelichting,
            "new_test3",
        )

        # invalid informatie_object required
        data = {
            "bijlagen": [
                {
                    # "informatieObject": "urn:nld:gemeenteutrecht:informatieobject:uuid:32af74f4-a7a2-4414-a9de-b50e35325cc6",
                    "toelichting": "new_test3",
                },
            ],
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "bijlagen"),
            {
                "name": "bijlagen",
                "code": "required",
                "reason": "bijlage must have a informatieObject.",
            },
        )

    def test_update_is_ingediend_door_json_schema(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        verzoek = VerzoekFactory.create(
            create_details=True,
            verzoek_type=verzoektype,
            niet_authentieke_persoonsgegevens=True,
        )
        self.assertEqual(
            verzoek.is_ingediend_door,
            {
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": "Jan",
                    "achternaam": "Jansen",
                    "geboortedatum": "1980-05-15",
                    "emailadres": "jan.jansen@example.com",
                    "telefoonnummer": "+31612345678",
                    "postadres": {"key": "value"},
                    "verblijfsadres": {"key": "value"},
                }
            },
        )
        detail_url = reverse(
            "verzoeken:verzoek-detail", kwargs={"uuid": str(verzoek.uuid)}
        )
        response = self.client.patch(
            detail_url,
            {
                "isIngediendDoor": {
                    "authentiekeVerwijzing": {"urn": "urn:example:12345"}
                },
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek = Verzoek.objects.get()
        self.assertEqual(
            verzoek.is_ingediend_door,
            {"authentiekeVerwijzing": {"urn": "urn:example:12345"}},
        )

        # set empty
        response = self.client.patch(detail_url, {"isIngediendDoor": {}})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek = Verzoek.objects.get()
        self.assertEqual(verzoek.is_ingediend_door, {})

        # check
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoek = Verzoek.objects.get()
        self.assertEqual(verzoek.is_ingediend_door, {})

        # invalid options
        response = self.client.patch(
            detail_url,
            {
                "isIngediendDoor": {"authentiekeVerwijzing": {}},
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "isIngediendDoor.authentiekeVerwijzing"),
            {
                "name": "isIngediendDoor.authentiekeVerwijzing",
                "code": "invalid-json-schema",
                "reason": "'urn' is a required property",
            },
        )

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
        self.assertEqual(len(response.data["invalid_params"]), 3)
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
        self.assertEqual(
            get_validation_errors(response, "version"),
            {
                "name": "version",
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
        self.assertFalse(Verzoek.objects.exists())
