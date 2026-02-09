import json

from django.urls import reverse, reverse_lazy
from django.utils import timezone

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from openvtb.accounts.tests.factories import UserFactory

from ..constants import SoortTaak, StatusTaak
from ..models import ExterneTaak
from .factories import FORM_IO, ExterneTaakFactory


@disable_admin_mfa()
class ExterneTaakAdminTests(WebTest):
    url = reverse_lazy("admin:taken_externetaak_add")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create(superuser=True)

    def setUp(self) -> None:
        super().setUp()
        self.app.set_user(self.user)

    def test_create_externe_taak_success(self):
        self.assertEqual(ExterneTaak.objects.count(), 0)

        response = self.app.get(self.url)
        form = response.forms.get("externetaak_form")

        form["titel"] = "test"
        form["status"] = StatusTaak.OPEN
        form["startdatum"] = timezone.now().date()
        form["handelings_perspectief"] = "test"
        form["einddatum_handelings_termijn"] = timezone.now().date()
        form["toelichting"] = "TEST TEST"
        form["taak_soort"] = SoortTaak.BETAALTAAK
        form["details"] = json.dumps(
            {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
        )
        form["is_toegewezen_aan"] = json.dumps(
            {
                "authentiekeVerwijzing": {
                    "urn": "urn:nld:brp:bsn:111222333",
                }
            }
        )

        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExterneTaak.objects.count(), 1)

    def test_update_version_schema(self):
        taak = ExterneTaakFactory.create(betaaltaak=True)
        self.assertEqual(ExterneTaak.objects.count(), 1)

        url = reverse("admin:taken_externetaak_change", args=[taak.id])
        response = self.app.get(url)
        form = response.forms.get("externetaak_form")
        form["taak_soort"] = SoortTaak.FORMULIERTAAK
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        error_list = response.html.find_all("ul", {"class": "errorlist"})
        self.assertEqual(
            error_list[0].get_text(strip=True),
            """{\'details\': ["Additional properties are not allowed (\'bedrag\', \'doelrekening\', \'transactieomschrijving\', \'valuta\' were unexpected)"]}""",
        )
        details = {
            "formulierDefinitie": FORM_IO,
            "voorinvullenGegevens": {
                "textField": "Test value",
            },
            "ontvangenGegevens": {
                "key": "value",
            },
        }

        form["details"] = json.dumps(details)
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExterneTaak.objects.count(), 1)
        self.assertEqual(ExterneTaak.objects.get().details, details)
