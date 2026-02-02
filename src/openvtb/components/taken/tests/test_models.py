import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from freezegun import freeze_time

from .factories import ExterneTaakFactory


@freeze_time("2026-01-01")
class ValidateExterneTaakModelTestCase(TestCase):
    def test_valid_datum_herinnering(self):
        # set datum_herinnering
        einddatum_handelings_termijn = timezone.now()
        datum_herinnering = timezone.now() - datetime.timedelta(days=10)
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
            datum_herinnering=datum_herinnering,
        )
        taak.full_clean()
        self.assertEqual(taak.datum_herinnering, datum_herinnering)

        # empty datum_herinnering
        einddatum_handelings_termijn = timezone.now()
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
        )
        taak.full_clean()
        self.assertEqual(
            taak.datum_herinnering,
            (
                taak.einddatum_handelings_termijn
                - datetime.timedelta(settings.TAKEN_DEFAULT_REMINDER_IN_DAYS)
            ),
        )

        # TAKEN_DEFAULT_REMINDER_IN_DAYS unset
        with override_settings(TAKEN_DEFAULT_REMINDER_IN_DAYS=0):
            einddatum_handelings_termijn = timezone.now()
            taak = ExterneTaakFactory.create(
                betaaltaak=True,
                einddatum_handelings_termijn=einddatum_handelings_termijn,
            )
            taak.full_clean()
            self.assertEqual(taak.datum_herinnering, None)

    def test_invalid_dates(self):
        # set datum_herinnering > einddatum_handelings_termijn
        einddatum_handelings_termijn = timezone.now()
        datum_herinnering = einddatum_handelings_termijn + datetime.timedelta(days=10)
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
            datum_herinnering=datum_herinnering,
        )
        with self.assertRaises(ValidationError) as error:
            taak.full_clean()
        self.assertTrue("einddatum_handelings_termijn" in error.exception.message_dict)

        # set startdatum > einddatum_handelings_termijn
        einddatum_handelings_termijn = timezone.now()
        startdatum = einddatum_handelings_termijn + datetime.timedelta(days=10)
        taak = ExterneTaakFactory.create(
            betaaltaak=True,
            einddatum_handelings_termijn=einddatum_handelings_termijn,
            startdatum=startdatum,
        )
        with self.assertRaises(ValidationError) as error:
            taak.full_clean()
        self.assertTrue("einddatum_handelings_termijn" in error.exception.message_dict)
