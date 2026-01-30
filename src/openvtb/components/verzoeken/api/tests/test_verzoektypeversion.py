import uuid
from datetime import date, timedelta

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.verzoeken.constants import VerzoekTypeVersionStatus
from openvtb.components.verzoeken.models import BijlageType, VerzoekType
from openvtb.components.verzoeken.tests.factories import (
    JSON_SCHEMA,
    VerzoekTypeFactory,
    VerzoekTypeVersionFactory,
)
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2025-01-01")
class VerzoekTypeVersionTests(APITestCase):
    list_url = reverse("verzoeken:verzoektype-list")
    maxDiff = None

    def test_detail_versions(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        VerzoekTypeVersionFactory.create_batch(4, verzoek_type=verzoektype)

        version_url = f"http://testserver{(reverse('verzoeken:verzoektypeversion-list', kwargs={'verzoektype_uuid': str(verzoektype.uuid)}))}"
        response = self.client.get(version_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # total = 1 + 4
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertEqual(response.json()["count"], 5)
        self.assertEqual(verzoektype.versions.count(), 5)

        # check last version
        self.assertEqual(verzoektype.last_version.version, 5)
        version_url = f"http://testserver{(reverse('verzoeken:verzoektypeversion-detail', kwargs={'verzoektype_uuid': str(verzoektype.uuid), 'verzoektype_version': verzoektype.last_version.version}))}"
        response = self.client.get(version_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": version_url,
                "version": 5,
                "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "status": "draft",
                "aanvraagGegevensSchema": verzoektype.last_version.aanvraag_gegevens_schema,
                "bijlageTypen": [],
                "aangemaaktOp": "2025-01-01",
                "gewijzigdOp": "2025-01-01",
                "beginGeldigheid": None,
                "eindeGeldigheid": None,
            },
        )

    def test_invalid_detail_versions(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)

        # not available version
        version_number = 100
        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": version_number,
            },
        )
        response = self.client.get(version_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # not available verzoektype
        verzoektype_uuid = str(uuid.uuid4())
        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": verzoektype_uuid,
                "verzoektype_version": verzoektype.last_version.version,
            },
        )
        response = self.client.get(version_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # invalid verzoektype uuid
        verzoektype_uuid = str(uuid.uuid4())
        version_url = reverse(
            "verzoeken:verzoektypeversion-list",
            kwargs={"verzoektype_uuid": "invalid-uuid-1234"},
        )
        response = self.client.get(version_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_version(self):
        verzoektype = VerzoekTypeFactory.create()
        self.assertEqual(verzoektype.versions.count(), 0)

        url = reverse(
            "verzoeken:verzoektypeversion-list",
            kwargs={"verzoektype_uuid": str(verzoektype.uuid)},
        )

        response = self.client.post(
            url,
            {"aanvraagGegevensSchema": JSON_SCHEMA},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoektype = VerzoekType.objects.get()

        self.assertEqual(verzoektype.versions.count(), 1)
        version = verzoektype.last_version
        self.assertEqual(version.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(version.version, 1)
        self.assertEqual(version.status, VerzoekTypeVersionStatus.DRAFT)
        self.assertEqual(version.aangemaakt_op, date(2025, 1, 1))
        self.assertEqual(version.gewijzigd_op, date(2025, 1, 1))
        self.assertEqual(version.begin_geldigheid, None)
        self.assertEqual(version.einde_geldigheid, None)

        # verzoekType is read_only, so is not used
        new_verzoektype = VerzoekTypeFactory.create()
        response = self.client.post(
            url,
            {
                "verzoekType": str(new_verzoektype.uuid),
                "aanvraagGegevensSchema": JSON_SCHEMA,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(verzoektype.versions.count(), 2)
        version = verzoektype.last_version
        self.assertEqual(version.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(version.version, 2)
        self.assertEqual(version.verzoek_type, verzoektype)

        # version is read_only, so is not used
        new_verzoektype = VerzoekTypeFactory.create()
        response = self.client.post(
            url,
            {
                "version": 100,
                "aanvraagGegevensSchema": JSON_SCHEMA,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(verzoektype.versions.count(), 3)
        version = verzoektype.last_version
        self.assertEqual(version.aanvraag_gegevens_schema, JSON_SCHEMA)
        # version auto generated
        self.assertEqual(version.version, 3)
        self.assertEqual(version.verzoek_type, verzoektype)

    def test_create_version_with_bijlage_typen(self):
        data = {
            "aanvraagGegevensSchema": JSON_SCHEMA,
            "bijlageTypen": [
                {
                    "informatieObjecttype": "urn:nld:gemeenteutrecht:informatieobjecttype:uuid:3c30bea0-cbf2-4fae-8d12-13b16395af1c",
                    "omschrijving": "test1",
                },
                {
                    "informatieObjecttype": "urn:nld:gemeenteutrecht:informatieobjecttype:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                    "omschrijving": "test2",
                },
            ],
        }
        verzoektype = VerzoekTypeFactory.create()
        self.assertEqual(verzoektype.versions.count(), 0)

        url = reverse(
            "verzoeken:verzoektypeversion-list",
            kwargs={"verzoektype_uuid": str(verzoektype.uuid)},
        )

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoektype = VerzoekType.objects.get()

        self.assertEqual(verzoektype.versions.count(), 1)
        version = verzoektype.last_version
        self.assertEqual(version.bijlage_typen.count(), 2)

    def test_invalid_create_version(self):
        verzoektype = VerzoekTypeFactory.create()
        self.assertEqual(verzoektype.versions.count(), 0)

        url = reverse(
            "verzoeken:verzoektypeversion-list",
            kwargs={"verzoektype_uuid": str(verzoektype.uuid)},
        )

        # empty POST
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "aanvraagGegevensSchema"),
            {
                "name": "aanvraagGegevensSchema",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(verzoektype.versions.count(), 0)

        # invalid schema
        response = self.client.post(
            url,
            {
                "aanvraagGegevensSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "invalid_type",
                        },
                    },
                },
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        error = get_validation_errors(response, "aanvraagGegevensSchema")
        self.assertEqual(error["name"], "aanvraagGegevensSchema")
        self.assertEqual(error["code"], "invalid-json-schema")

    def test_update_version(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": verzoektype.last_version.version,
            },
        )

        # empty PATCH
        response = self.client.patch(version_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # PATCH new_json_schema
        new_json_schema = {
            "type": "object",
            "title": "Tree",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "required": ["new_field"],
            "properties": {"new_field": {"type": "string"}},
        }
        response = self.client.patch(
            version_url, {"aanvraagGegevensSchema": new_json_schema}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()
        version = verzoektype.last_version

        self.assertNotEqual(version.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(version.aanvraag_gegevens_schema, new_json_schema)

        # empty PUT
        response = self.client.put(version_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "aanvraagGegevensSchema"),
            {
                "name": "aanvraagGegevensSchema",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )

        # PUT JSON_SCHEMA
        response = self.client.put(version_url, {"aanvraagGegevensSchema": JSON_SCHEMA})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()
        version = verzoektype.last_version

        self.assertNotEqual(version.aanvraag_gegevens_schema, new_json_schema)
        self.assertEqual(version.aanvraag_gegevens_schema, JSON_SCHEMA)

    def test_update_read_only_fields_version(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": verzoektype.last_version.version,
            },
        )
        # verzoekType is read_only, so is not used
        new_verzoektype = VerzoekTypeFactory.create()
        response = self.client.patch(
            version_url, {"verzoekType": str(new_verzoektype.uuid)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(verzoektype.versions.count(), 1)
        version = verzoektype.last_version
        self.assertEqual(version.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(version.version, 1)
        self.assertEqual(version.verzoek_type, verzoektype)

        # version is read_only, so is not used
        new_verzoektype = VerzoekTypeFactory.create()
        response = self.client.patch(version_url, {"version": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(verzoektype.versions.count(), 1)
        version = verzoektype.last_version
        self.assertEqual(version.aanvraag_gegevens_schema, JSON_SCHEMA)
        # version auto generated
        self.assertEqual(version.version, 1)
        self.assertEqual(version.verzoek_type, verzoektype)

    def test_update_status_version(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": verzoektype.last_version.version,
            },
        )

        # DRAFT -> PUBLISHED
        self.assertEqual(
            verzoektype.last_version.status, VerzoekTypeVersionStatus.DRAFT
        )
        response = self.client.patch(
            version_url, {"status": VerzoekTypeVersionStatus.PUBLISHED}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoektype.refresh_from_db()
        self.assertEqual(
            verzoektype.last_version.status, VerzoekTypeVersionStatus.PUBLISHED
        )

        # PUBLISHED -> DRAFT
        self.assertEqual(
            verzoektype.last_version.status, VerzoekTypeVersionStatus.PUBLISHED
        )
        response = self.client.patch(
            version_url, {"status": VerzoekTypeVersionStatus.DRAFT}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "status"),
            {
                "name": "status",
                "code": "non-draft-version-update",
                "reason": "Alleen `draft` kunnen worden gewijzigd.",
            },
        )
        verzoektype.refresh_from_db()
        self.assertEqual(
            verzoektype.last_version.status, VerzoekTypeVersionStatus.PUBLISHED
        )

    def test_automatically_update_expired_date(self):
        verzoektype = VerzoekTypeFactory.create()
        v1 = VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        self.assertEqual(v1.version, 1)
        v2 = VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        self.assertEqual(v2.version, 2)

        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": verzoektype.last_version.version,
            },
        )

        # V2 DRAFT -> PUBLISHED
        self.assertEqual(v2.status, VerzoekTypeVersionStatus.DRAFT)
        response = self.client.patch(
            version_url, {"status": VerzoekTypeVersionStatus.PUBLISHED}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        v1.refresh_from_db()
        v2.refresh_from_db()

        self.assertEqual(v2.status, VerzoekTypeVersionStatus.PUBLISHED)
        self.assertFalse(v2.is_expired)

        # v1 must be expired
        self.assertTrue(v1.is_expired)

    def test_manually_update_expired_date(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        self.assertFalse(verzoektype.last_version.is_expired)

        # today
        response = self.client.patch(
            reverse(
                "verzoeken:verzoektypeversion-detail",
                kwargs={
                    "verzoektype_uuid": str(verzoektype.uuid),
                    "verzoektype_version": verzoektype.last_version.version,
                },
            ),
            {"eindeGeldigheid": date.today()},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()
        self.assertTrue(verzoektype.last_version.is_expired)

        # future
        response = self.client.patch(
            reverse(
                "verzoeken:verzoektypeversion-detail",
                kwargs={
                    "verzoektype_uuid": str(verzoektype.uuid),
                    "verzoektype_version": verzoektype.last_version.version,
                },
            ),
            {"eindeGeldigheid": date.today() + timedelta(1)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()

        # expire tomorrow
        self.assertFalse(verzoektype.last_version.is_expired)

    def test_update_with_bijlage_typen(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": verzoektype.last_version.version,
            },
        )
        BijlageType.objects.create(
            verzoek_type_version=verzoektype.last_version,
            informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
            omschrijving="description1",
        )
        BijlageType.objects.create(
            verzoek_type_version=verzoektype.last_version,
            informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:3c30bea0-cbf2-4fae-8d12-13b16395af1c",
            omschrijving="description2",
        )

        self.assertEqual(verzoektype.last_version.bijlage_typen.count(), 2)

        # create in this case, because doesn't exist with this informatieObjecttype
        response = self.client.patch(
            version_url,
            {
                "bijlageTypen": [
                    {
                        "informatieObjecttype": "urn:nld:gemeenteutrecht:informatieobjecttype:uuid:dc367113-5a7b-4418-8d4e-14ae78720b70",
                        "omschrijving": "description3",
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()

        self.assertEqual(verzoektype.last_version.bijlage_typen.count(), 3)

        # check before and later `omschrijving`
        self.assertEqual(
            verzoektype.last_version.bijlage_typen.get(
                informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:dc367113-5a7b-4418-8d4e-14ae78720b70"
            ).omschrijving,
            "description3",
        )
        # update in this case, because it exist with this informatie_objecttype
        response = self.client.patch(
            version_url,
            {
                "bijlageTypen": [
                    {
                        "informatieObjecttype": "urn:nld:gemeenteutrecht:informatieobjecttype:uuid:dc367113-5a7b-4418-8d4e-14ae78720b70",
                        "omschrijving": "new_description_3",
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()

        self.assertEqual(verzoektype.last_version.bijlage_typen.count(), 3)
        self.assertEqual(
            verzoektype.last_version.bijlage_typen.get(
                informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:dc367113-5a7b-4418-8d4e-14ae78720b70"
            ).omschrijving,
            "new_description_3",
        )

        # invalid informatie_objecttype required
        response = self.client.patch(
            version_url,
            {
                "bijlageTypen": [
                    {
                        # "informatieObjecttype": "urn:nld:gemeenteutrecht:informatieobjecttype:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
                        "omschrijving": "new_description_3",
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        verzoektype.refresh_from_db()

        self.assertEqual(verzoektype.last_version.bijlage_typen.count(), 3)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "bijlageTypen"),
            {
                "name": "bijlageTypen",
                "code": "required",
                "reason": "bijlageType must have a informatieObjecttype.",
            },
        )

    def test_destroy_version(self):
        verzoektype = VerzoekTypeFactory.create(create_version=True)
        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": verzoektype.last_version.version,
            },
        )
        response = self.client.get(version_url)

        self.assertEqual(verzoektype.versions.count(), 1)
        response = self.client.delete(version_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(version_url)
        verzoektype.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(verzoektype.versions.count(), 0)

        VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        verzoektype.refresh_from_db()
        self.assertEqual(verzoektype.versions.count(), 1)

        # DRAFT -> PUBLISHED
        version = verzoektype.versions.first()
        version.status = VerzoekTypeVersionStatus.PUBLISHED
        version.save()

        version_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_version": verzoektype.last_version.version,
            },
        )
        response = self.client.delete(version_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "nonFieldErrors"),
            {
                "name": "nonFieldErrors",
                "code": "non-draft-version-destroy",
                "reason": "Only draft versions can be destroyed",
            },
        )
