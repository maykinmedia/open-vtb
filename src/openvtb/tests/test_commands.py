from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from rest_framework.authtoken.models import Token

from openvtb.components.berichten.models import Bericht
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.verzoeken.models import Verzoek


class GenerateDataTests(TestCase):
    def test_creates_count_per_resource(self):
        call_command("generate_data", count=4, stdout=StringIO())

        self.assertEqual(Verzoek.objects.count(), 4)
        self.assertEqual(ExterneTaak.objects.count(), 4)
        self.assertEqual(Bericht.objects.count(), 4)
        self.assertTrue(Token.objects.filter(key="performance_token").exists())

    def test_only_selected_resources(self):
        call_command("generate_data", count=2, resources=["taken"], stdout=StringIO())

        self.assertEqual(ExterneTaak.objects.count(), 2)
        self.assertFalse(Verzoek.objects.exists())
        self.assertFalse(Bericht.objects.exists())

    def test_multiple_resources(self):
        call_command(
            "generate_data",
            count=3,
            resources=["verzoeken", "berichten"],
            stdout=StringIO(),
        )

        self.assertEqual(Verzoek.objects.count(), 3)
        self.assertEqual(Bericht.objects.count(), 3)
        self.assertFalse(ExterneTaak.objects.exists())

    def test_rerun_replaces_load_test_user(self):
        for _ in range(2):
            call_command(
                "generate_data", count=1, resources=["taken"], stdout=StringIO()
            )

        self.assertEqual(
            get_user_model().objects.filter(username="performance_token").count(), 1
        )
        self.assertEqual(Token.objects.filter(key="performance_token").count(), 1)

    def test_unknown_resource(self):
        call_command("generate_data", count=1, resources=["unknown"], stdout=StringIO())
        self.assertFalse(ExterneTaak.objects.exists())
        self.assertFalse(Verzoek.objects.exists())
        self.assertFalse(Bericht.objects.exists())
