from io import StringIO

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings

from openvtb.accounts.tests.factories import UserFactory

from ..models import User


class CreateInitialSuperuserTests(TestCase):
    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_create_initial_superuser_command(self):
        call_command(
            "createinitialsuperuser",
            "--generate-password",
            "--email-password-reset",
            username="maykin",
            email="support@maykinmedia.nl",
            stdout=StringIO(),
        )
        user = User.objects.get()

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertEqual(
            sent_mail.subject,
            f"Your admin user for {settings.PROJECT_NAME} (example.com)",
        )
        self.assertEqual(sent_mail.recipients(), ["support@maykinmedia.nl"])

    @override_settings(ALLOWED_HOSTS=[])
    def test_create_initial_superuser_command_allowed_hosts_empty(self):
        call_command(
            "createinitialsuperuser",
            "--generate-password",
            "--email-password-reset",
            username="maykin",
            email="support@maykinmedia.nl",
            stdout=StringIO(),
        )
        user = User.objects.get()

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertEqual(
            sent_mail.subject,
            f"Your admin user for {settings.PROJECT_NAME} (unknown url)",
        )
        self.assertEqual(sent_mail.recipients(), ["support@maykinmedia.nl"])

    @override_settings(ALLOWED_HOSTS=["*"])  # test all
    def test_create_superuser_already_exists(self):
        self.assertEqual(User.objects.count(), 0)
        UserFactory.create(superuser=True, username="maykin")

        self.assertEqual(User.objects.count(), 1)

        call_command(
            "createinitialsuperuser",
            "--generate-password",
            "--email-password-reset",
            username="maykin",
            email="support@maykinmedia.nl",
            stdout=StringIO(),
        )

        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        self.assertEqual(user.username, "maykin")
