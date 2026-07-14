import uuid

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.verzoeken.constants import VerwerkStatus
from openvtb.components.verzoeken.tests.factories import (
    VerzoekFactory,
    VerzoekTypeFactory,
)
from openvtb.utils.api_testcase import APITestCase


class VerzoekFilterTest(APITestCase):
    list_url = reverse("verzoeken:verzoek-list")

    def setUp(self):
        super().setUp()

        self.verzoek_type_a = VerzoekTypeFactory.create(create_versie=True)
        self.verzoek_type_b = VerzoekTypeFactory.create(create_versie=True)

        self.verzoek_a = VerzoekFactory.create(
            verzoek_type=self.verzoek_type_a,
            initiator="urn:maykin:123",
            mede_initiator="urn:maykin:456",
            versie=1,
            verwerk_status=VerwerkStatus.GEREGISTREERD,
        )
        self.verzoek_b = VerzoekFactory.create(
            verzoek_type=self.verzoek_type_b,
            initiator="urn:maykin:789",
            mede_initiator="urn:maykin:012",
            versie=2,
            verwerk_status=VerwerkStatus.VERWERKT,
        )
        self.verzoek_c = VerzoekFactory.create(
            verzoek_type=self.verzoek_type_a,
            initiator="urn:maykin:345",
            mede_initiator="urn:maykin:678",
            versie=3,
            verwerk_status=VerwerkStatus.VERWERKT,
        )

    def test_filter_uuid(self):
        response = self.client.get(self.list_url, {"uuid": str(self.verzoek_a.uuid)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_a.uuid))

        response = self.client.get(self.list_url, {"uuid": str(self.verzoek_b.uuid)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_b.uuid))

        # random uuid
        response = self.client.get(self.list_url, {"uuid": str(uuid.uuid4())})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 0)

        # invalid uuid
        response = self.client.get(self.list_url, {"uuid": "test"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "uuid"),
            {
                "name": "uuid",
                "code": "invalid",
                "reason": "Voer een geldige UUID in.",
            },
        )

    def test_filter_verzoek_type_uuid(self):
        response = self.client.get(
            self.list_url, {"verzoekType__uuid": str(self.verzoek_type_a.uuid)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        uuids = {result["uuid"] for result in data["results"]}
        self.assertEqual(uuids, {str(self.verzoek_a.uuid), str(self.verzoek_c.uuid)})

        # invalid uuid
        response = self.client.get(self.list_url, {"verzoekType__uuid": "test"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "verzoekType__uuid"),
            {
                "name": "verzoekType__uuid",
                "code": "invalid",
                "reason": "Voer een geldige UUID in.",
            },
        )

    def test_filter_initiator(self):
        response = self.client.get(self.list_url, {"initiator": "urn:maykin:123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_a.uuid))

        # not found
        response = self.client.get(self.list_url, {"initiator": "urn:maykin:test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

        response = self.client.get(self.list_url, {"initiator": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_filter_mede_initiator(self):
        response = self.client.get(self.list_url, {"medeInitiator": "urn:maykin:456"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_a.uuid))

        response = self.client.get(self.list_url, {"medeInitiator": "urn:maykin:test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

        response = self.client.get(self.list_url, {"medeInitiator": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_filter_versie(self):
        response = self.client.get(self.list_url, {"versie": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_a.uuid))

        # not found
        response = self.client.get(self.list_url, {"versie": 1000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

        # invalid versie
        response = self.client.get(self.list_url, {"versie": "test"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "versie"),
            {
                "name": "versie",
                "code": "invalid",
                "reason": "Voer een getal in.",
            },
        )

    def test_filter_verwerk_status(self):
        response = self.client.get(
            self.list_url, {"verwerkStatus": VerwerkStatus.GEREGISTREERD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_a.uuid))

        response = self.client.get(
            self.list_url, {"verwerkStatus": VerwerkStatus.VERWERKT}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        uuids = {result["uuid"] for result in data["results"]}
        self.assertEqual(uuids, {str(self.verzoek_b.uuid), str(self.verzoek_c.uuid)})

        # invalid verwerkStatus
        response = self.client.get(self.list_url, {"verwerkStatus": "test"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "verwerkStatus"),
            {
                "name": "verwerkStatus",
                "code": "invalid_choice",
                "reason": "Selecteer een geldige keuze. test is geen beschikbare keuze.",
            },
        )


class VerzoekTypeFilterTest(APITestCase):
    list_url = reverse("verzoeken:verzoektype-list")

    def setUp(self):
        super().setUp()
        self.verzoek_type_a = VerzoekTypeFactory.create(
            naam="Verzoektype A",
            omschrijving="Dit is een algemene omschrijving voor type A",
        )
        self.verzoek_type_b = VerzoekTypeFactory.create(
            naam="Verzoektype B",
            omschrijving="Specifieke omschrijving met details",
        )
        self.verzoek_type_c = VerzoekTypeFactory.create(
            naam="Verzoektype C",
            omschrijving="Nog een algemene omschrijving",
        )

    def test_filter_uuid(self):
        response = self.client.get(
            self.list_url, {"uuid": str(self.verzoek_type_a.uuid)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_type_a.uuid))

        response = self.client.get(
            self.list_url, {"uuid": str(self.verzoek_type_b.uuid)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_type_b.uuid))

        # random uuid
        response = self.client.get(self.list_url, {"uuid": str(uuid.uuid4())})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 0)

        # invalid uuid
        response = self.client.get(self.list_url, {"uuid": "test"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "uuid"),
            {
                "name": "uuid",
                "code": "invalid",
                "reason": "Voer een geldige UUID in.",
            },
        )

    def test_filter_naam(self):
        response = self.client.get(self.list_url, {"naam": "Verzoektype A"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(self.verzoek_type_a.uuid))

        response = self.client.get(self.list_url, {"naam": "Verzoektype TEST"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_filter_omschrijving_icontains(self):
        response = self.client.get(
            self.list_url, {"omschrijving__icontains": "algemene"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        uuids = {result["uuid"] for result in data["results"]}
        self.assertEqual(
            uuids,
            {str(self.verzoek_type_a.uuid), str(self.verzoek_type_c.uuid)},
        )

        response = self.client.get(
            self.list_url, {"omschrijving__icontains": "ALGEMENE"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)

        response = self.client.get(
            self.list_url, {"omschrijving__icontains": "nonexistent"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 0)
