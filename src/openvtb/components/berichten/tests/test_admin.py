import json

from django.urls import reverse_lazy
from django.utils import timezone

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from openvtb.accounts.tests.factories import UserFactory

from ..models import Bericht


@disable_admin_mfa()
class BerichtenAdminTests(WebTest):
    url = reverse_lazy("admin:berichten_bericht_add")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create(superuser=True)

    def setUp(self) -> None:
        super().setUp()
        self.app.set_user(self.user)

    def test_create_bericht_success(self):
        self.assertEqual(Bericht.objects.count(), 0)

        response = self.app.get(self.url)

        form = response.forms.get("bericht_form")

        form["onderwerp"] = "Test"
        form["bericht_tekst"] = "Test"
        form["publicatiedatum_0"] = timezone.now().date()
        form["publicatiedatum_1"] = timezone.now().time()
        form["ontvanger"] = "urn:nld:brp:bsn:111222333"
        form["geopend_op_0"] = timezone.now().date()
        form["geopend_op_1"] = timezone.now().time()
        form["referentie"] = "12345678"
        form["bericht_type"] = "12345678"
        form["handelings_perspectief"] = "Test"
        form["einddatum_handelings_termijn_0"] = timezone.now().date()
        form["einddatum_handelings_termijn_1"] = timezone.now().time()
        form["is_gerelateerd_aan"] = json.dumps(
            [{"urn": "urn:nld:gemeenteutrecht:zaak:zaaknummer:000350165"}]
        )
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Bericht.objects.count(), 1)

    def test_create_bericht_invalid_is_gerelateerd_aan_field(self):
        response = self.app.get(self.url)
        form = response.forms.get("bericht_form")
        form["onderwerp"] = "Test"
        form["bericht_tekst"] = "Test"
        form["publicatiedatum_0"] = timezone.now().date()
        form["publicatiedatum_1"] = timezone.now().time()
        form["ontvanger"] = "urn:nld:brp:bsn:111222333"
        form["geopend_op_0"] = timezone.now().date()
        form["geopend_op_1"] = timezone.now().time()
        form["referentie"] = "12345678"
        form["bericht_type"] = "12345678"
        form["handelings_perspectief"] = "Test"
        form["einddatum_handelings_termijn_0"] = timezone.now().date()
        form["einddatum_handelings_termijn_1"] = timezone.now().time()

        form["is_gerelateerd_aan"] = json.dumps([{"test": ""}])
        response = form.submit()

        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertEqual(
            error_list[0].get_text(strip=True),
            """{'is_gerelateerd_aan.0': ["Additional properties are not allowed ('test' was unexpected)"]}""",
        )
