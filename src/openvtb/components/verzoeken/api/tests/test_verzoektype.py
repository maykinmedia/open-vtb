from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.verzoeken.constants import VerzoekTypeVersionStatus
from openvtb.components.verzoeken.models import VerzoekType
from openvtb.components.verzoeken.tests.factories import (
    VerzoekTypeFactory,
    VerzoekTypeVersionFactory,
)
from openvtb.utils.api_testcase import APITestCase


class VerzoekTypeTests(APITestCase):
    list_url = reverse("verzoeken:verzoektype-list")
    maxDiff = None

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(VerzoekType.objects.exists())

        VerzoekTypeFactory.create(create_version=True)
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
                        "url": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                        "urn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                        "uuid": str(verzoektype.uuid),
                        "versions": [
                            {
                                "url": f"http://testserver{(reverse('verzoeken:verzoektypeversion-detail', kwargs={'verzoektype_uuid': str(verzoektype.uuid), 'verzoektype_version': verzoektype.last_version.version}))}",
                                "version": verzoektype.last_version.version,
                                "status": verzoektype.last_version.status,
                            },
                        ],
                        "naam": verzoektype.naam,
                        "toelichting": verzoektype.toelichting,
                    }
                ],
            },
        )

        VerzoekTypeFactory.create(create_version=True)
        VerzoekTypeFactory.create(create_version=True)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertEqual(VerzoekType.objects.all().count(), 3)

    def test_detail(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        detail_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "urn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                "uuid": str(verzoektype.uuid),
                "versions": [
                    {
                        "url": f"http://testserver{(reverse('verzoeken:verzoektypeversion-detail', kwargs={'verzoektype_uuid': str(verzoektype.uuid), 'verzoektype_version': 2}))}",
                        "version": 2,
                        "status": VerzoekTypeVersionStatus.DRAFT,
                    },
                    {
                        "url": f"http://testserver{(reverse('verzoeken:verzoektypeversion-detail', kwargs={'verzoektype_uuid': str(verzoektype.uuid), 'verzoektype_version': 1}))}",
                        "version": 1,
                        "status": VerzoekTypeVersionStatus.DRAFT,
                    },
                ],
                "naam": verzoektype.naam,
                "toelichting": verzoektype.toelichting,
            },
        )

    def test_valid_create(self):
        data = {
            "naam": "string",
            "toelichting": "string",
        }

        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(VerzoekType.objects.all().count(), 1)
        verzoektype = VerzoekType.objects.get()

        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "urn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                "uuid": str(verzoektype.uuid),
                "versions": [],
                "naam": "string",
                "toelichting": "string",
            },
        )

        self.assertEqual(verzoektype.naam, "string")
        self.assertEqual(verzoektype.toelichting, "string")
        self.assertEqual(verzoektype.last_version, None)

    def test_invalid_create(self):
        self.assertFalse(VerzoekType.objects.exists())
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")

        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "naam"),
            {
                "name": "naam",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertFalse(VerzoekType.objects.exists())

    def test_valid_update(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        detail_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
        )
        response = self.client.get(detail_url)

        # empty PATCH
        data = {}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # PATCH
        data = {"naam": "new_naam", "toelichting": "new_toelichting"}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoektype = VerzoekType.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "urn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                "uuid": str(verzoektype.uuid),
                "versions": [
                    {
                        "url": f"http://testserver{(reverse('verzoeken:verzoektypeversion-detail', kwargs={'verzoektype_uuid': str(verzoektype.uuid), 'verzoektype_version': verzoektype.last_version.version}))}",
                        "version": verzoektype.last_version.version,
                        "status": verzoektype.last_version.status,
                    },
                ],
                "naam": "new_naam",
                "toelichting": "new_toelichting",
            },
        )

        # PUT
        data = {
            "naam": "new_naam_2",
        }
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoektype = VerzoekType.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "urn": f"urn:maykin:verzoeken:verzoektype:{str(verzoektype.uuid)}",
                "uuid": str(verzoektype.uuid),
                "versions": [
                    {
                        "url": f"http://testserver{(reverse('verzoeken:verzoektypeversion-detail', kwargs={'verzoektype_uuid': str(verzoektype.uuid), 'verzoektype_version': verzoektype.last_version.version}))}",
                        "version": verzoektype.last_version.version,
                        "status": verzoektype.last_version.status,
                    },
                ],
                "naam": "new_naam_2",
                "toelichting": "new_toelichting",
            },
        )

    def test_invalid_update(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        detail_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
        )
        response = self.client.get(detail_url)
        verzoektype = VerzoekType.objects.get()

        # PUT
        data = {}
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")

        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "naam"),
            {
                "name": "naam",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_destroy(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        detail_url = reverse(
            "verzoeken:verzoektype-detail", kwargs={"uuid": str(verzoektype.uuid)}
        )
        response = self.client.get(detail_url)

        self.assertEqual(VerzoekType.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(VerzoekType.objects.exists())
