import json
from datetime import date

from django.urls import reverse, reverse_lazy

from django_webtest import WebTest
from freezegun import freeze_time
from maykin_2fa.test import disable_admin_mfa

from openvtb.accounts.tests.factories import UserFactory

from ..constants import VerzoektypeOpvolging, VerzoekTypeVersionStatus
from ..models import VerzoekType, VerzoekTypeVersion
from .factories import VerzoekTypeFactory, VerzoekTypeVersionFactory

JSON_SCHEMA = {
    "type": "object",
    "title": "Tree",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "required": ["diameter"],
    "properties": {
        "diameter": {
            "type": "integer",
            "description": "size in cm.",
        },
        "extra": {
            "type": "object",
            "title": "extra",
            "keys": {},
            "additionalProperties": True,
        },
    },
    "additionalProperties": False,
}


@disable_admin_mfa()
class VerzoekTypeAddTests(WebTest):
    url = reverse_lazy("admin:verzoeken_verzoektype_add")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create(superuser=True)

    def setUp(self) -> None:
        super().setUp()
        self.app.set_user(self.user)

    def test_create_verzoektype_success(self):
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(VerzoekTypeVersion.objects.count(), 0)

        response = self.app.get(self.url)
        form = response.forms.get("verzoektype_form")
        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = json.dumps(JSON_SCHEMA)
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(VerzoekType.objects.count(), 1)
        self.assertEqual(VerzoekTypeVersion.objects.count(), 1)

        verzoek_type = VerzoekType.objects.get()

        self.assertEqual(verzoek_type.naam, "test")
        self.assertEqual(verzoek_type.opvolging, VerzoektypeOpvolging.NIET_TOT_ZAAK)

        verzoek_type_version = verzoek_type.last_version

        self.assertEqual(verzoek_type_version.version, 1)
        self.assertEqual(verzoek_type_version.aanvraag_gegevens_schema, JSON_SCHEMA)
        self.assertEqual(verzoek_type_version.status, VerzoekTypeVersionStatus.DRAFT)

    def test_create_verzoektype_required_fields(self):
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(VerzoekTypeVersion.objects.count(), 0)

        response = self.app.get(self.url)
        form = response.forms.get("verzoektype_form")
        response = form.submit()

        self.assertEqual(response.status_code, 200)

        error_list = response.html.find_all("ul", {"class": "errorlist"})

        self.assertEqual(
            str(error_list[0]),
            """<ul class="errorlist" id="id_naam_error"><li>Dit veld is vereist.</li></ul>""",
        )
        self.assertEqual(
            str(error_list[1]),
            """<ul class="errorlist" id="id_versions-0-aanvraag_gegevens_schema_error"><li>Dit veld is vereist.</li></ul>""",
        )
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(VerzoekTypeVersion.objects.count(), 0)

    def test_create_verzoektype_invalid_json_schema(self):
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(VerzoekTypeVersion.objects.count(), 0)

        response = self.app.get(self.url)

        form = response.forms.get("verzoektype_form")
        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = "test"
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertEqual(
            str(error_list[0]),
            """<ul class="errorlist" id="id_versions-0-aanvraag_gegevens_schema_error"><li>Voer een geldige JSON in.</li></ul>""",
        )

        form = response.forms.get("verzoektype_form")
        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = {}
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertEqual(
            str(error_list[0]),
            """<ul class="errorlist" id="id_versions-0-aanvraag_gegevens_schema_error"><li>Dit veld is vereist.</li></ul>""",
        )

        form = response.forms.get("verzoektype_form")
        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = None
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertEqual(
            str(error_list[0]),
            """<ul class="errorlist" id="id_versions-0-aanvraag_gegevens_schema_error"><li>Dit veld is vereist.</li></ul>""",
        )

        form = response.forms.get("verzoektype_form")
        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = json.dumps(
            {
                "title": "Tree",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "any",
            }
        )
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertIn(
            "'any' is not valid under any of the given schemas",
            str(error_list[0]),
        )

        form = response.forms.get("verzoektype_form")
        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = json.dumps(
            {
                "title": False,
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
            }
        )
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertIn(
            "False is not of type 'string'",
            str(error_list[0]),
        )
        form = response.forms.get("verzoektype_form")
        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = json.dumps(
            {
                "title": "title",
                "$schema": "test",
                "type": "object",
            }
        )
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertIn(
            "'test' is not a 'uri'",
            str(error_list[0]),
        )

        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(VerzoekTypeVersion.objects.count(), 0)

    def test_display_only_last_version(self):
        verzoek_type = VerzoekTypeFactory.create()
        VerzoekTypeVersionFactory.create_batch(3, verzoek_type=verzoek_type)
        url = reverse("admin:verzoeken_verzoektype_change", args=[verzoek_type.id])

        response = self.app.get(url)
        form = response.forms.get("verzoektype_form")

        self.assertEqual(int(form["versions-TOTAL_FORMS"].value), 1)
        self.assertEqual(int(form["versions-0-id"].value), verzoek_type.last_version.id)

    def test_update_version_schema(self):
        verzoek_type = VerzoekTypeFactory.create()
        VerzoekTypeVersionFactory.create(verzoek_type=verzoek_type)
        url = reverse("admin:verzoeken_verzoektype_change", args=[verzoek_type.id])

        response = self.app.get(url)
        form = response.forms.get("verzoektype_form")

        self.assertEqual(int(form["versions-TOTAL_FORMS"].value), 1)
        self.assertEqual(int(form["versions-0-id"].value), verzoek_type.last_version.id)

        self.assertEqual(
            verzoek_type.last_version.status, VerzoekTypeVersionStatus.DRAFT
        )
        # default value from factory
        self.assertEqual(
            form["versions-0-aanvraag_gegevens_schema"].value,
            json.dumps(verzoek_type.last_version.aanvraag_gegevens_schema),
        )

        form["naam"] = "test"
        form["versions-0-aanvraag_gegevens_schema"] = json.dumps(JSON_SCHEMA)
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(VerzoekType.objects.count(), 1)
        self.assertEqual(VerzoekTypeVersion.objects.count(), 1)

        self.assertEqual(
            verzoek_type.last_version.status, VerzoekTypeVersionStatus.DRAFT
        )
        # new json_schema
        self.assertEqual(
            form["versions-0-aanvraag_gegevens_schema"].value,
            json.dumps(JSON_SCHEMA),
        )

    def test_update_publishd_version_schema(self):
        verzoek_type = VerzoekTypeFactory.create()
        VerzoekTypeVersionFactory.create(verzoek_type=verzoek_type)
        url = reverse("admin:verzoeken_verzoektype_change", args=[verzoek_type.id])

        VerzoekTypeVersion.objects.filter(pk=verzoek_type.last_version.id).update(
            status=VerzoekTypeVersionStatus.PUBLISHED
        )

        self.assertEqual(
            verzoek_type.last_version.status, VerzoekTypeVersionStatus.PUBLISHED
        )

        response = self.app.get(url)
        form = response.forms.get("verzoektype_form")
        # aanvraag_gegevens_schema readonly field
        self.assertNotIn("versions-0-aanvraag_gegevens_schema", form.fields)
