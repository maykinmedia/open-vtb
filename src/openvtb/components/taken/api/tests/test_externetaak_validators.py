import datetime

from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.utils.api_testcase import APITestCase


class ExterneTaakValidationTests(APITestCase):
    list_url = reverse("taken:externetaak-list")
    details = {
        "bedrag": "11",
        "transactieomschrijving": "test",
        "doelrekening": {
            "naam": "test",
            "code": "123-ABC",
            "iban": "NL12BANK34567890",
        },
    }

    def test_invalid_create_type_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "test",
            "taakSoort": SoortTaak.BETAALTAAK.value,
            "startdatum": datetime.date(2026, 1, 10),  # end < start
            "einddatumHandelingsTermijn": datetime.date(2025, 1, 10),
            "details": self.details,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            get_validation_errors(response, "einddatumHandelingsTermijn"),
            {
                "name": "einddatumHandelingsTermijn",
                "code": "date-mismatch",
                "reason": "startdatum should be before einddatum_handelings_termijn.",
            },
        )
        self.assertFalse(ExterneTaak.objects.exists())
