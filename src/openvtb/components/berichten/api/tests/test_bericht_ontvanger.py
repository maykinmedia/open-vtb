import datetime

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.berichten.models import BerichtOntvanger
from openvtb.components.berichten.tests.factories import BerichtOntvangerFactory
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-01-01")
class BerichtOntvangerTests(APITestCase):
    list_url = reverse("berichten:berichtontvanger-list")
    maxDiff = None

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(BerichtOntvanger.objects.exists())

        # create ontvanger
        BerichtOntvangerFactory.create()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(BerichtOntvanger.objects.all().count(), 1)

        ontvanger = BerichtOntvanger.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
                        "urn": f"urn:maykin:berichten:berichtontvanger:{str(ontvanger.uuid)}",
                        "uuid": str(ontvanger.uuid),
                        "geadresseerde": ontvanger.geadresseerde,
                        "geopendOp": ontvanger.geopend_op.isoformat().replace(
                            "+00:00", "Z"
                        ),
                        "geopend": ontvanger.geopend,
                    },
                ],
            },
        )

        BerichtOntvangerFactory.create()
        BerichtOntvangerFactory.create()
        BerichtOntvangerFactory.create()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 4)
        self.assertEqual(BerichtOntvanger.objects.all().count(), 4)

    def test_list_pagination_pagesize_param(self):
        BerichtOntvangerFactory.create_batch(10)
        response = self.client.get(self.list_url, {"pageSize": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(response.json()["count"], 10)
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertEqual(
            data["next"], f"http://testserver{self.list_url}?page=2&pageSize=5"
        )

    def test_detail(self):
        ontvanger = BerichtOntvangerFactory.create()
        detail_url = reverse(
            "berichten:berichtontvanger-detail", kwargs={"uuid": str(ontvanger.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
                "urn": f"urn:maykin:berichten:berichtontvanger:{str(ontvanger.uuid)}",
                "uuid": str(ontvanger.uuid),
                "geadresseerde": ontvanger.geadresseerde,
                "geopendOp": ontvanger.geopend_op.isoformat().replace("+00:00", "Z"),
                "geopend": ontvanger.geopend,
            },
        )

    def test_valid_create(self):
        self.assertFalse(BerichtOntvanger.objects.exists())
        data = {
            "geadresseerde": "urn:maykin:test1",
            "geopendOp": datetime.datetime.now(),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BerichtOntvanger.objects.all().count(), 1)

        ontvanger = BerichtOntvanger.objects.get()

        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
                "urn": f"urn:maykin:berichten:berichtontvanger:{str(ontvanger.uuid)}",
                "uuid": str(ontvanger.uuid),
                "geadresseerde": ontvanger.geadresseerde,
                "geopendOp": ontvanger.geopend_op.isoformat().replace("+00:00", "Z"),
                "geopend": ontvanger.geopend,
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertFalse(BerichtOntvanger.objects.exists())
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Invalid input.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "geadresseerde"),
            {
                "name": "geadresseerde",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

    def test_update_partial(self):
        ontvanger = BerichtOntvangerFactory.create()
        detail_url = reverse(
            "berichten:berichtontvanger-detail", kwargs={"uuid": str(ontvanger.uuid)}
        )

        # empty PATCH
        data = {}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
                "urn": f"urn:maykin:berichten:berichtontvanger:{str(ontvanger.uuid)}",
                "uuid": str(ontvanger.uuid),
                "geadresseerde": ontvanger.geadresseerde,
                "geopendOp": ontvanger.geopend_op.isoformat().replace("+00:00", "Z"),
                "geopend": ontvanger.geopend,
            },
        )
        # PATCH geadresseerde field
        data = {"geadresseerde": "urn:maykin:new12345"}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ontvanger = BerichtOntvanger.objects.get()
        self.assertEqual(ontvanger.geadresseerde, "urn:maykin:new12345")

    def test_update(self):
        ontvanger = BerichtOntvangerFactory.create()

        detail_url = reverse(
            "berichten:berichtontvanger-detail", kwargs={"uuid": str(ontvanger.uuid)}
        )

        # all required PUT fields
        data = {"geadresseerde": "urn:maykin:new12345"}
        response = self.client.put(detail_url, data)
        ontvanger = BerichtOntvanger.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('berichten:berichtontvanger-detail', kwargs={'uuid': str(ontvanger.uuid)})}",
                "urn": f"urn:maykin:berichten:berichtontvanger:{str(ontvanger.uuid)}",
                "uuid": str(ontvanger.uuid),
                "geadresseerde": ontvanger.geadresseerde,
                "geopendOp": ontvanger.geopend_op.isoformat().replace("+00:00", "Z"),
                "geopend": ontvanger.geopend,
            },
        )

    def test_destroy(self):
        ontvanger = BerichtOntvangerFactory.create()

        detail_url = reverse(
            "berichten:berichtontvanger-detail", kwargs={"uuid": str(ontvanger.uuid)}
        )

        self.assertEqual(BerichtOntvanger.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(BerichtOntvanger.objects.exists())
