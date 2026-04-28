from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from freezegun import freeze_time

from openvtb.components.taken.constants import StatusTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory

from ..cloudevents import EXTERNETAAK_HERINNERD, EXTERNETAAK_VERLOPEN
from ..tasks import send_taak_events

MOCKED_CLOUDEVENT_ID = "f347fd1f-dac1-4870-9dd0-f6c00edf4bf7"
NOTIFICATIONS_SOURCE = "openvtb-test"
FROZEN_TIME = "2026-01-01"
FROZEN_TIME_Z = "2026-01-01T00:00:00Z"


@freeze_time(FROZEN_TIME)
@patch("notifications_api_common.tasks.send_cloudevent.delay")
@patch("notifications_api_common.cloudevents.uuid.uuid4", lambda: MOCKED_CLOUDEVENT_ID)
@override_settings(
    NOTIFICATIONS_SOURCE=NOTIFICATIONS_SOURCE, CELERY_TASK_ALWAYS_EAGER=True
)
class CloudEventsTaskTakenTest(TestCase):
    @override_settings(ENABLE_CLOUD_EVENTS=False)
    def test_no_cloudevent_when_disabled(self, mock_process_cloudevent):
        taak = ExterneTaakFactory.create(
            formuliertaak=True,
            einddatum_handelings_termijn=timezone.now() - timedelta(days=1),
        )

        self.assertFalse(taak.is_handelings_termijn_verzonden)

        with self.captureOnCommitCallbacks(execute=True):
            send_taak_events()

        mock_process_cloudevent.assert_not_called()
        self.assertFalse(taak.is_handelings_termijn_verzonden)

    def test_cloudevent_not_open_taaken(self, mock_process_cloudevent):
        taak = ExterneTaakFactory.create(
            formuliertaak=True,
            datum_herinnering=timezone.now() - timedelta(days=1),
            is_handelings_termijn_verzonden=True,
            status=StatusTaak.VERWERKT,
        )
        with self.captureOnCommitCallbacks(execute=True):
            send_taak_events()

        mock_process_cloudevent.assert_not_called()

        # reopen task
        taak.status = StatusTaak.OPEN
        taak.save()
        with self.captureOnCommitCallbacks(execute=True):
            send_taak_events()

        mock_process_cloudevent.assert_called_once()
        payload = mock_process_cloudevent.call_args[0][0]
        self.assertEqual(payload["type"], EXTERNETAAK_HERINNERD)  # send event

    def test_cloudevent_reminder(self, mock_process_cloudevent):
        with self.subTest("past_reminders"):
            taak = ExterneTaakFactory.create(
                formuliertaak=True,
                datum_herinnering=timezone.now() - timedelta(days=1),
                is_handelings_termijn_verzonden=True,
            )
            self.assertFalse(taak.is_herinnering_verzonden)

            # first run
            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            taak.refresh_from_db()

            assert mock_process_cloudevent.call_count == 1
            self.assertTrue(taak.is_herinnering_verzonden)

            # second run, no process cloudevent
            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            taak.refresh_from_db()

            assert mock_process_cloudevent.call_count == 1
            self.assertTrue(taak.is_herinnering_verzonden)

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_HERINNERD)

            # third run, reset and check no calls
            mock_process_cloudevent.reset_mock()
            assert mock_process_cloudevent.call_count == 0

            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()
            taak.refresh_from_db()

            assert mock_process_cloudevent.call_count == 0
            self.assertTrue(taak.is_herinnering_verzonden)

            # fourth run, new taak in past
            old_taak = ExterneTaakFactory.create(
                formuliertaak=True,
                datum_herinnering=timezone.now() - timedelta(days=1),
                is_handelings_termijn_verzonden=True,
            )
            self.assertFalse(old_taak.is_herinnering_verzonden)
            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            assert mock_process_cloudevent.call_count == 1  # only one for the new taak
            old_taak.refresh_from_db()

            self.assertTrue(old_taak.is_herinnering_verzonden)

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_HERINNERD)

        mock_process_cloudevent.reset_mock()

        with self.subTest("future_reminders"):
            now = timezone.now()
            date_1 = now + timedelta(days=1)
            date_10 = now + timedelta(days=10)
            ExterneTaakFactory.create(
                formuliertaak=True,
                datum_herinnering=date_1,
                is_handelings_termijn_verzonden=True,
            )
            ExterneTaakFactory.create(
                formuliertaak=True,
                datum_herinnering=date_10,
                is_handelings_termijn_verzonden=True,
            )

            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            mock_process_cloudevent.assert_not_called()

            with freeze_time((date_1 + timedelta(days=1)).isoformat()):
                with self.captureOnCommitCallbacks(execute=True):
                    send_taak_events()

            assert mock_process_cloudevent.call_count == 1

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_HERINNERD)

            with freeze_time((date_10 + timedelta(days=1)).isoformat()):
                with self.captureOnCommitCallbacks(execute=True):
                    send_taak_events()

            assert mock_process_cloudevent.call_count == 2

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_HERINNERD)

    def test_cloudevent_expired(self, mock_process_cloudevent):
        with self.subTest("past_expiration"):
            taak = ExterneTaakFactory.create(
                formuliertaak=True,
                einddatum_handelings_termijn=timezone.now() - timedelta(days=1),
                is_herinnering_verzonden=True,
            )
            self.assertFalse(taak.is_handelings_termijn_verzonden)

            # first run
            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            taak.refresh_from_db()

            assert mock_process_cloudevent.call_count == 1
            self.assertTrue(taak.is_handelings_termijn_verzonden)

            # second run, no process cloudevent
            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            taak.refresh_from_db()

            assert mock_process_cloudevent.call_count == 1
            self.assertTrue(taak.is_handelings_termijn_verzonden)

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_VERLOPEN)

            # third run, reset and check no calls
            mock_process_cloudevent.reset_mock()
            assert mock_process_cloudevent.call_count == 0

            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()
            taak.refresh_from_db()

            assert mock_process_cloudevent.call_count == 0
            self.assertTrue(taak.is_handelings_termijn_verzonden)

            # fourth run, new taak in past
            old_taak = ExterneTaakFactory.create(
                formuliertaak=True,
                einddatum_handelings_termijn=timezone.now() - timedelta(days=1),
                is_herinnering_verzonden=True,
            )
            self.assertFalse(old_taak.is_handelings_termijn_verzonden)
            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            assert mock_process_cloudevent.call_count == 1  # only one for the new taak
            old_taak.refresh_from_db()

            self.assertTrue(old_taak.is_handelings_termijn_verzonden)

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_VERLOPEN)

        mock_process_cloudevent.reset_mock()

        with self.subTest("future_expiration"):
            now = timezone.now()
            date_1 = now + timedelta(days=1)
            date_10 = now + timedelta(days=10)
            ExterneTaakFactory.create(
                formuliertaak=True,
                einddatum_handelings_termijn=date_1,
                is_herinnering_verzonden=True,
            )
            ExterneTaakFactory.create(
                formuliertaak=True,
                einddatum_handelings_termijn=date_10,
                is_herinnering_verzonden=True,
            )

            with self.captureOnCommitCallbacks(execute=True):
                send_taak_events()

            mock_process_cloudevent.assert_not_called()

            with freeze_time((date_1 + timedelta(days=1)).isoformat()):
                with self.captureOnCommitCallbacks(execute=True):
                    send_taak_events()

            assert mock_process_cloudevent.call_count == 1

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_VERLOPEN)

            with freeze_time((date_10 + timedelta(days=1)).isoformat()):
                with self.captureOnCommitCallbacks(execute=True):
                    send_taak_events()

            assert mock_process_cloudevent.call_count == 2

            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_VERLOPEN)

    @patch("openvtb.components.taken.tasks.send_taak_cloudevent", side_effect=Exception)
    def test_does_not_publish_if_event_fails(self, m, mock_send):
        taak = ExterneTaakFactory.create(
            formuliertaak=True,
            einddatum_handelings_termijn=timezone.now() - timedelta(days=1),
            is_herinnering_verzonden=True,
        )

        self.assertFalse(taak.is_handelings_termijn_verzonden)

        with self.assertRaises(Exception):
            send_taak_events()

        taak.refresh_from_db()
        self.assertFalse(taak.is_handelings_termijn_verzonden)
