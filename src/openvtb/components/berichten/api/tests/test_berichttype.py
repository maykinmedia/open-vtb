from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.berichten.models import BerichtType
from openvtb.components.berichten.tests.factories import (
    BerichtTypeFactory,
)
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-01-01")
class BerichtTypeTests(APITestCase):
    list_url = reverse("berichten:berichttype-list")
    maxDiff = None

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(BerichtType.objects.exists())

        # create berichtType
        BerichtTypeFactory.create(create_bijlagetype=True)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(BerichtType.objects.all().count(), 1)

        bericht_type = BerichtType.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(bericht_type.uuid)})}",
                        "urn": f"urn:maykin:berichten:berichttype:{str(bericht_type.uuid)}",
                        "uuid": str(bericht_type.uuid),
                        "bijlageTypen": [
                            {
                                "informatieObjecttype": bericht_type.bijlage_typen.first().informatie_objecttype,
                                "omschrijving": bericht_type.bijlage_typen.first().omschrijving,
                            }
                        ],
                        "handelingsPerspectief": bericht_type.handelings_perspectief,
                        "mijnOverheidBerichtenbox": bericht_type.mijn_overheid_berichtenbox,
                        "mijnOverheidBerichtenboxType": bericht_type.mijn_overheid_berichtenbox_type,
                        "verantwoordelijkeOrganisatie": bericht_type.verantwoordelijke_organisatie,
                    }
                ],
            },
        )

        BerichtTypeFactory.create()
        BerichtTypeFactory.create()
        BerichtTypeFactory.create()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 4)
        self.assertEqual(BerichtType.objects.all().count(), 4)

    def test_list_pagination_pagesize_param(self):
        BerichtTypeFactory.create_batch(10)
        response = self.client.get(self.list_url, {"pageSize": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(response.json()["count"], 10)
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertEqual(
            data["next"], f"http://testserver{self.list_url}?page=2&pageSize=5"
        )

    def test_detail(self):
        # create berichtType
        bericht_type = BerichtTypeFactory.create(create_bijlagetype=True)
        detail_url = reverse(
            "berichten:berichttype-detail", kwargs={"uuid": str(bericht_type.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(bericht_type.uuid)})}",
                "urn": f"urn:maykin:berichten:berichttype:{str(bericht_type.uuid)}",
                "uuid": str(bericht_type.uuid),
                "bijlageTypen": [
                    {
                        "informatieObjecttype": bericht_type.bijlage_typen.first().informatie_objecttype,
                        "omschrijving": bericht_type.bijlage_typen.first().omschrijving,
                    }
                ],
                "handelingsPerspectief": bericht_type.handelings_perspectief,
                "mijnOverheidBerichtenbox": bericht_type.mijn_overheid_berichtenbox,
                "mijnOverheidBerichtenboxType": bericht_type.mijn_overheid_berichtenbox_type,
                "verantwoordelijkeOrganisatie": bericht_type.verantwoordelijke_organisatie,
            },
        )

    def test_valid_create(self):
        self.assertFalse(BerichtType.objects.exists())

        data = {
            "handelingsPerspectief": "incasso",
            "mijnOverheidBerichtenbox": False,
            "mijnOverheidBerichtenboxType": "test",
            "verantwoordelijkeOrganisatie": "urn:nld:gemeenteutrecht:product:00011111",
            "bijlageTypen": [
                {
                    "informatieObjecttype": "urn:maykin:test1",
                    "omschrijving": "test1",
                },
                {
                    "informatieObjecttype": "urn:maykin:test2",
                    "omschrijving": "test2",
                },
            ],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BerichtType.objects.all().count(), 1)

        bericht_type = BerichtType.objects.get()
        bijlage_type1 = bericht_type.bijlage_typen.get(
            informatie_objecttype="urn:maykin:test1"
        )
        bijlage_type2 = bericht_type.bijlage_typen.get(
            informatie_objecttype="urn:maykin:test2"
        )
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(bericht_type.uuid)})}",
                "urn": f"urn:maykin:berichten:berichttype:{str(bericht_type.uuid)}",
                "uuid": str(bericht_type.uuid),
                "bijlageTypen": [
                    {
                        "informatieObjecttype": bijlage_type1.informatie_objecttype,
                        "omschrijving": bijlage_type1.omschrijving,
                    },
                    {
                        "informatieObjecttype": bijlage_type2.informatie_objecttype,
                        "omschrijving": bijlage_type2.omschrijving,
                    },
                ],
                "handelingsPerspectief": bericht_type.handelings_perspectief,
                "mijnOverheidBerichtenbox": bericht_type.mijn_overheid_berichtenbox,
                "mijnOverheidBerichtenboxType": bericht_type.mijn_overheid_berichtenbox_type,
                "verantwoordelijkeOrganisatie": bericht_type.verantwoordelijke_organisatie,
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertFalse(BerichtType.objects.exists())
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 2)
        self.assertEqual(
            get_validation_errors(response, "mijnOverheidBerichtenbox"),
            {
                "name": "mijnOverheidBerichtenbox",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "verantwoordelijkeOrganisatie"),
            {
                "name": "verantwoordelijkeOrganisatie",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_invalid_create_bijlage_typen_duplicated(self):
        self.assertFalse(BerichtType.objects.exists())
        data = {
            "handelingsPerspectief": "incasso",
            "mijnOverheidBerichtenbox": False,
            "mijnOverheidBerichtenboxType": "test",
            "verantwoordelijkeOrganisatie": "urn:nld:gemeenteutrecht:product:00011111",
            "bijlageTypen": [
                {
                    "informatieObjecttype": "urn:maykin:test1",
                    "omschrijving": "test1",
                },
                {
                    "informatieObjecttype": "urn:maykin:test1",
                    "omschrijving": "test1",
                },
            ],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "bijlageTypen"),
            {
                "name": "bijlageTypen",
                "code": "unique",
                "reason": "BijlageType with the specified informatieObjecttype already exists.",
            },
        )

    def test_valid_update(self):
        bericht_type = BerichtTypeFactory.create()
        detail_url = reverse(
            "berichten:berichttype-detail", kwargs={"uuid": str(bericht_type.uuid)}
        )
        response = self.client.get(detail_url)

        # empty PATCH
        data = {}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # PATCH
        data = {"verantwoordelijkeOrganisatie": "urn:test:new:value"}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(bericht_type.uuid)})}",
                "urn": f"urn:maykin:berichten:berichttype:{str(bericht_type.uuid)}",
                "uuid": str(bericht_type.uuid),
                "bijlageTypen": [],
                "handelingsPerspectief": bericht_type.handelings_perspectief,
                "mijnOverheidBerichtenbox": bericht_type.mijn_overheid_berichtenbox,
                "mijnOverheidBerichtenboxType": bericht_type.mijn_overheid_berichtenbox_type,
                "verantwoordelijkeOrganisatie": "urn:test:new:value",
            },
        )

        # PATCH bijlageTypen
        data = {
            "bijlageTypen": [
                {"informatieObjecttype": "urn:maykin:test1", "omschrijving": "test1"}
            ]
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(bericht_type.uuid)})}",
                "urn": f"urn:maykin:berichten:berichttype:{str(bericht_type.uuid)}",
                "uuid": str(bericht_type.uuid),
                "bijlageTypen": [
                    {
                        "informatieObjecttype": "urn:maykin:test1",
                        "omschrijving": "test1",
                    },
                ],
                "handelingsPerspectief": bericht_type.handelings_perspectief,
                "mijnOverheidBerichtenbox": bericht_type.mijn_overheid_berichtenbox,
                "mijnOverheidBerichtenboxType": bericht_type.mijn_overheid_berichtenbox_type,
                "verantwoordelijkeOrganisatie": "urn:test:new:value",
            },
        )

        data = {
            "bijlageTypen": [
                {
                    "informatieObjecttype": "urn:maykin:test1",
                    "omschrijving": "new_text_same_informatieobjecttype",
                },
                {
                    "informatieObjecttype": "urn:maykin:test2",
                    "omschrijving": "complete_new_value_informatieobjecttype",
                },
            ]
        }
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(bericht_type.uuid)})}",
                "urn": f"urn:maykin:berichten:berichttype:{str(bericht_type.uuid)}",
                "uuid": str(bericht_type.uuid),
                "bijlageTypen": [
                    {
                        "informatieObjecttype": "urn:maykin:test1",
                        "omschrijving": "new_text_same_informatieobjecttype",
                    },
                    {
                        "informatieObjecttype": "urn:maykin:test2",
                        "omschrijving": "complete_new_value_informatieobjecttype",
                    },
                ],
                "handelingsPerspectief": bericht_type.handelings_perspectief,
                "mijnOverheidBerichtenbox": bericht_type.mijn_overheid_berichtenbox,
                "mijnOverheidBerichtenboxType": bericht_type.mijn_overheid_berichtenbox_type,
                "verantwoordelijkeOrganisatie": "urn:test:new:value",
            },
        )

        # PUT
        data = {
            "handelingsPerspectief": "incasso",
            "mijnOverheidBerichtenbox": False,
            "mijnOverheidBerichtenboxType": "test",
            "verantwoordelijkeOrganisatie": "urn:nld:gemeenteutrecht:product:00011111",
            "bijlageTypen": [
                {
                    "informatieObjecttype": "urn:maykin:test1",
                    "omschrijving": "test1",
                },
                {
                    "informatieObjecttype": "urn:maykin:test2",
                    "omschrijving": "test2",
                },
            ],
        }
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bericht_type = BerichtType.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichttype-detail', kwargs={'uuid': str(bericht_type.uuid)})}",
                "urn": f"urn:maykin:berichten:berichttype:{str(bericht_type.uuid)}",
                "uuid": str(bericht_type.uuid),
                "bijlageTypen": [
                    {
                        "informatieObjecttype": "urn:maykin:test1",
                        "omschrijving": "test1",
                    },
                    {
                        "informatieObjecttype": "urn:maykin:test2",
                        "omschrijving": "test2",
                    },
                ],
                "handelingsPerspectief": "incasso",
                "mijnOverheidBerichtenbox": False,
                "mijnOverheidBerichtenboxType": "test",
                "verantwoordelijkeOrganisatie": "urn:nld:gemeenteutrecht:product:00011111",
            },
        )

    def test_destroy(self):
        bericht_type = BerichtTypeFactory.create()
        detail_url = reverse(
            "berichten:berichttype-detail", kwargs={"uuid": str(bericht_type.uuid)}
        )
        response = self.client.get(detail_url)

        self.assertEqual(BerichtType.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(BerichtType.objects.exists())
