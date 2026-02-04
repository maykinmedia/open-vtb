from django.urls import reverse_lazy
from django.utils import timezone

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from openvtb.accounts.tests.factories import UserFactory

from ..models import Bericht, BerichtOntvanger
from .factories import BerichtOntvangerFactory


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

    def test_create_bericht_ontvanger_success(self):
        self.assertEqual(Bericht.objects.count(), 0)
        self.assertEqual(BerichtOntvanger.objects.count(), 0)

        response = self.app.get(reverse_lazy("admin:berichten_berichtontvanger_add"))

        form = response.forms.get("berichtontvanger_form")

        form["geadresseerde"] = "urn:nld:brp.bsn:111222333"
        form["geopend_op_0"] = timezone.now().date()
        form["geopend_op_1"] = timezone.now().time()

        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Bericht.objects.count(), 0)
        self.assertEqual(BerichtOntvanger.objects.count(), 1)

    def test_create_bericht_success(self):
        BerichtOntvangerFactory.create()
        self.assertEqual(Bericht.objects.count(), 0)
        self.assertEqual(BerichtOntvanger.objects.count(), 1)

        response = self.app.get(self.url)

        form = response.forms.get("bericht_form")

        form["onderwerp"] = "Test"
        form["bericht_tekst"] = "Test"
        form["publicatiedatum_0"] = timezone.now().date()
        form["publicatiedatum_1"] = timezone.now().time()
        form["ontvanger"] = BerichtOntvanger.objects.get().pk
        form["referentie"] = "12345678"
        form["bericht_type"] = "12345678"
        form["handelings_perspectief"] = "Test"
        form["einddatum_handelings_termijn_0"] = timezone.now().date()
        form["einddatum_handelings_termijn_1"] = timezone.now().time()

        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Bericht.objects.count(), 1)
        self.assertEqual(BerichtOntvanger.objects.count(), 1)
