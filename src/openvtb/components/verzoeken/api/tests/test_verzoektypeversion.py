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


@freeze_time("2026-01-01")
class VerzoekTypeversieTests(APITestCase):
    list_url = reverse("verzoeken:verzoektype-list")
    maxDiff = None

    def test_detail_versies(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        VerzoekTypeVersionFactory.create_batch(4, verzoek_type=verzoektype)

        versie_url = f"http://testserver{(reverse('verzoeken:verzoektypeversion-list', kwargs={'verzoektype_uuid': str(verzoektype.uuid)}))}"
        response = self.client.get(versie_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # total = 1 + 4
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertEqual(response.json()["count"], 5)
        self.assertEqual(verzoektype.versies.count(), 5)

        # check last versie
        self.assertEqual(verzoektype.last_versie.versie, 5)
        versie_url = f"http://testserver{(reverse('verzoeken:verzoektypeversion-detail', kwargs={'verzoektype_uuid': str(verzoektype.uuid), 'verzoektype_versie': verzoektype.last_versie.versie}))}"
        response = self.client.get(versie_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": versie_url,
                "versie": 5,
                "verzoekType": f"http://testserver{reverse('verzoeken:verzoektype-detail', kwargs={'uuid': str(verzoektype.uuid)})}",
                "status": "draft",
                "aanvraagGegevensSchema": verzoektype.last_versie.aanvraag_gegevens_schema,
                "bijlageTypen": [],
                "aangemaaktOp": "2026-01-01",
                "gewijzigdOp": "2026-01-01",
                "beginGeldigheid": None,
                "eindeGeldigheid": None,
            },
        )

    def test_invalid_detail_versies(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)

        # not available versie
        versie_number = 100
        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": versie_number,
            },
        )
        response = self.client.get(versie_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # not available verzoektype
        verzoektype_uuid = str(uuid.uuid4())
        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": verzoektype_uuid,
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )
        response = self.client.get(versie_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # invalid verzoektype uuid
        verzoektype_uuid = str(uuid.uuid4())
        versie_url = reverse(
            "verzoeken:verzoektypeversion-list",
            kwargs={"verzoektype_uuid": "invalid-uuid-1234"},
        )
        response = self.client.get(versie_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_versie(self):
        verzoektype = VerzoekTypeFactory.create()
        self.assertEqual(verzoektype.versies.count(), 0)

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

        self.assertEqual(verzoektype.versies.count(), 1)
        versie = verzoektype.last_versie
        self.assertEqual(versie.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(versie.versie, 1)
        self.assertEqual(versie.status, VerzoekTypeVersionStatus.DRAFT)
        self.assertEqual(versie.aangemaakt_op, date(2026, 1, 1))
        self.assertEqual(versie.gewijzigd_op, date(2026, 1, 1))
        self.assertEqual(versie.begin_geldigheid, None)
        self.assertEqual(versie.einde_geldigheid, None)

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
        self.assertEqual(verzoektype.versies.count(), 2)
        versie = verzoektype.last_versie
        self.assertEqual(versie.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(versie.versie, 2)
        self.assertEqual(versie.verzoek_type, verzoektype)

        # versie is read_only, so is not used
        new_verzoektype = VerzoekTypeFactory.create()
        response = self.client.post(
            url,
            {
                "versie": 100,
                "aanvraagGegevensSchema": JSON_SCHEMA,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(verzoektype.versies.count(), 3)
        versie = verzoektype.last_versie
        self.assertEqual(versie.aanvraag_gegevens_schema, JSON_SCHEMA)
        # versie auto generated
        self.assertEqual(versie.versie, 3)
        self.assertEqual(versie.verzoek_type, verzoektype)

    def test_create_versie_with_bijlage_typen(self):
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
        self.assertEqual(verzoektype.versies.count(), 0)

        url = reverse(
            "verzoeken:verzoektypeversion-list",
            kwargs={"verzoektype_uuid": str(verzoektype.uuid)},
        )

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verzoektype = VerzoekType.objects.get()

        self.assertEqual(verzoektype.versies.count(), 1)
        versie = verzoektype.last_versie
        self.assertEqual(versie.bijlage_typen.count(), 2)

    def test_invalid_create_versie(self):
        verzoektype = VerzoekTypeFactory.create()
        self.assertEqual(verzoektype.versies.count(), 0)

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
        self.assertEqual(verzoektype.versies.count(), 0)

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

    def test_update_versie(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )

        # empty PATCH
        response = self.client.patch(versie_url, {})
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
            versie_url, {"aanvraagGegevensSchema": new_json_schema}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()
        versie = verzoektype.last_versie

        self.assertNotEqual(versie.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(versie.aanvraag_gegevens_schema, new_json_schema)

        # empty PUT
        response = self.client.put(versie_url, {})
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
        response = self.client.put(versie_url, {"aanvraagGegevensSchema": JSON_SCHEMA})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()
        versie = verzoektype.last_versie

        self.assertNotEqual(versie.aanvraag_gegevens_schema, new_json_schema)
        self.assertEqual(versie.aanvraag_gegevens_schema, JSON_SCHEMA)

    def test_update_read_only_fields_versie(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )
        # verzoekType is read_only, so is not used
        new_verzoektype = VerzoekTypeFactory.create()
        response = self.client.patch(
            versie_url, {"verzoekType": str(new_verzoektype.uuid)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(verzoektype.versies.count(), 1)
        versie = verzoektype.last_versie
        self.assertEqual(versie.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(versie.versie, 1)
        self.assertEqual(versie.verzoek_type, verzoektype)

        # versie is read_only, so is not used
        new_verzoektype = VerzoekTypeFactory.create()
        response = self.client.patch(versie_url, {"versie": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(verzoektype.versies.count(), 1)
        versie = verzoektype.last_versie
        self.assertEqual(versie.aanvraag_gegevens_schema, JSON_SCHEMA)
        # versie auto generated
        self.assertEqual(versie.versie, 1)
        self.assertEqual(versie.verzoek_type, verzoektype)

    def test_update_status_versie(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )

        # DRAFT -> PUBLISHED
        self.assertEqual(verzoektype.last_versie.status, VerzoekTypeVersionStatus.DRAFT)
        response = self.client.patch(
            versie_url, {"status": VerzoekTypeVersionStatus.PUBLISHED}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verzoektype.refresh_from_db()
        self.assertEqual(
            verzoektype.last_versie.status, VerzoekTypeVersionStatus.PUBLISHED
        )

        # PUBLISHED -> DRAFT
        self.assertEqual(
            verzoektype.last_versie.status, VerzoekTypeVersionStatus.PUBLISHED
        )
        response = self.client.patch(
            versie_url, {"status": VerzoekTypeVersionStatus.DRAFT}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "status"),
            {
                "name": "status",
                "code": "non-draft-versie-update",
                "reason": "Alleen `draft` kunnen worden gewijzigd.",
            },
        )
        verzoektype.refresh_from_db()
        self.assertEqual(
            verzoektype.last_versie.status, VerzoekTypeVersionStatus.PUBLISHED
        )

    def test_automatically_update_expired_date(self):
        verzoektype = VerzoekTypeFactory.create()
        v1 = VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        self.assertEqual(v1.versie, 1)
        v2 = VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        self.assertEqual(v2.versie, 2)

        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )

        # V2 DRAFT -> PUBLISHED
        self.assertEqual(v2.status, VerzoekTypeVersionStatus.DRAFT)
        response = self.client.patch(
            versie_url, {"status": VerzoekTypeVersionStatus.PUBLISHED}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        v1.refresh_from_db()
        v2.refresh_from_db()

        self.assertEqual(v2.status, VerzoekTypeVersionStatus.PUBLISHED)
        self.assertFalse(v2.is_expired)

        # v1 must be expired
        self.assertTrue(v1.is_expired)

    def test_manually_update_expired_date(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        self.assertFalse(verzoektype.last_versie.is_expired)

        # today
        response = self.client.patch(
            reverse(
                "verzoeken:verzoektypeversion-detail",
                kwargs={
                    "verzoektype_uuid": str(verzoektype.uuid),
                    "verzoektype_versie": verzoektype.last_versie.versie,
                },
            ),
            {"eindeGeldigheid": date.today()},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()
        self.assertTrue(verzoektype.last_versie.is_expired)

        # future
        response = self.client.patch(
            reverse(
                "verzoeken:verzoektypeversion-detail",
                kwargs={
                    "verzoektype_uuid": str(verzoektype.uuid),
                    "verzoektype_versie": verzoektype.last_versie.versie,
                },
            ),
            {"eindeGeldigheid": date.today() + timedelta(1)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verzoektype.refresh_from_db()

        # expire tomorrow
        self.assertFalse(verzoektype.last_versie.is_expired)

    def test_update_with_bijlage_typen(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )
        BijlageType.objects.create(
            verzoek_type_versie=verzoektype.last_versie,
            informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:717815f6-1939-4fd2-93f0-83d25bad154e",
            omschrijving="description1",
        )
        BijlageType.objects.create(
            verzoek_type_versie=verzoektype.last_versie,
            informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:3c30bea0-cbf2-4fae-8d12-13b16395af1c",
            omschrijving="description2",
        )

        self.assertEqual(verzoektype.last_versie.bijlage_typen.count(), 2)

        # create in this case, because doesn't exist with this informatieObjecttype
        response = self.client.patch(
            versie_url,
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

        self.assertEqual(verzoektype.last_versie.bijlage_typen.count(), 3)

        # check before and later `omschrijving`
        self.assertEqual(
            verzoektype.last_versie.bijlage_typen.get(
                informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:dc367113-5a7b-4418-8d4e-14ae78720b70"
            ).omschrijving,
            "description3",
        )
        # update in this case, because it exist with this informatie_objecttype
        response = self.client.patch(
            versie_url,
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

        self.assertEqual(verzoektype.last_versie.bijlage_typen.count(), 3)
        self.assertEqual(
            verzoektype.last_versie.bijlage_typen.get(
                informatie_objecttype="urn:nld:gemeenteutrecht:informatieobjecttype:uuid:dc367113-5a7b-4418-8d4e-14ae78720b70"
            ).omschrijving,
            "new_description_3",
        )

        # invalid informatie_objecttype required
        response = self.client.patch(
            versie_url,
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

        self.assertEqual(verzoektype.last_versie.bijlage_typen.count(), 3)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "bijlageTypen"),
            {
                "name": "bijlageTypen",
                "code": "required",
                "reason": "bijlageType must have a informatieObjecttype.",
            },
        )

    def test_destroy_versie(self):
        verzoektype = VerzoekTypeFactory.create(create_versie=True)
        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )
        response = self.client.get(versie_url)

        self.assertEqual(verzoektype.versies.count(), 1)
        response = self.client.delete(versie_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(versie_url)
        verzoektype.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(verzoektype.versies.count(), 0)

        VerzoekTypeVersionFactory.create(verzoek_type=verzoektype)
        verzoektype.refresh_from_db()
        self.assertEqual(verzoektype.versies.count(), 1)

        # DRAFT -> PUBLISHED
        versie = verzoektype.versies.first()
        versie.status = VerzoekTypeVersionStatus.PUBLISHED
        versie.save()

        versie_url = reverse(
            "verzoeken:verzoektypeversion-detail",
            kwargs={
                "verzoektype_uuid": str(verzoektype.uuid),
                "verzoektype_versie": verzoektype.last_versie.versie,
            },
        )
        response = self.client.delete(versie_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "nonFieldErrors"),
            {
                "name": "nonFieldErrors",
                "code": "non-draft-versie-destroy",
                "reason": "Only draft versies can be destroyed",
            },
        )
