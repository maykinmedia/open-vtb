from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from freezegun.api import freeze_time

from ..cloudevents import BERICHT_GEPUBLICEERD
from ..tasks import send_published_berichten
from .factories import BerichtFactory

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
class PublishedBerichtenTest(TestCase):
    @override_settings(ENABLE_CLOUD_EVENTS=False)
    def test_no_cloudevent_when_disabled(self, mock_process_cloudevent):
        bericht = BerichtFactory.create(
            publicatiedatum=timezone.now() + timedelta(days=1)
        )

        self.assertFalse(bericht.is_gepubliceerd)

        with self.captureOnCommitCallbacks(execute=True):
            send_published_berichten()

        mock_process_cloudevent.assert_not_called()
        self.assertFalse(bericht.is_gepubliceerd)

    def test_check_past_publicatiedatum(self, mock_process_cloudevent):
        bericht = BerichtFactory.create(
            publicatiedatum=timezone.now() - timedelta(days=1)
        )

        self.assertFalse(bericht.is_gepubliceerd)

        # first run
        with self.captureOnCommitCallbacks(execute=True):
            send_published_berichten()

        bericht.refresh_from_db()

        assert mock_process_cloudevent.call_count == 1
        self.assertTrue(bericht.is_gepubliceerd)

        # second run, no process cloudevent
        with self.captureOnCommitCallbacks(execute=True):
            send_published_berichten()

        bericht.refresh_from_db()

        assert mock_process_cloudevent.call_count == 1
        self.assertTrue(bericht.is_gepubliceerd)

        payload = mock_process_cloudevent.call_args[0][0]

        self.assertEqual(
            payload,
            {
                "id": MOCKED_CLOUDEVENT_ID,
                "source": NOTIFICATIONS_SOURCE,
                "specversion": "1.0",
                "type": BERICHT_GEPUBLICEERD,
                "subject": str(bericht.uuid),
                "time": FROZEN_TIME_Z,
                "dataref": None,
                "datacontenttype": "application/json",
                "data": {
                    "onderwerp": bericht.onderwerp,
                    "publicatiedatum": bericht.publicatiedatum.isoformat(),
                    "ontvanger": bericht.ontvanger,
                },
            },
        )

        # third run, reset and check no calls
        mock_process_cloudevent.reset_mock()
        assert mock_process_cloudevent.call_count == 0

        with self.captureOnCommitCallbacks(execute=True):
            send_published_berichten()
        bericht.refresh_from_db()

        assert mock_process_cloudevent.call_count == 0  # no cloud events are being sent
        self.assertTrue(bericht.is_gepubliceerd)

        # fourth run, new bericht in past
        old_bericht = BerichtFactory.create(
            publicatiedatum=timezone.now() - timedelta(days=2)
        )
        self.assertFalse(old_bericht.is_gepubliceerd)
        with self.captureOnCommitCallbacks(execute=True):
            send_published_berichten()

        assert mock_process_cloudevent.call_count == 1
        old_bericht.refresh_from_db()

        self.assertTrue(old_bericht.is_gepubliceerd)

        payload = mock_process_cloudevent.call_args[0][0]
        self.assertEqual(
            payload,
            {
                "id": MOCKED_CLOUDEVENT_ID,
                "source": NOTIFICATIONS_SOURCE,
                "specversion": "1.0",
                "type": BERICHT_GEPUBLICEERD,
                "subject": str(old_bericht.uuid),
                "time": FROZEN_TIME_Z,
                "dataref": None,
                "datacontenttype": "application/json",
                "data": {
                    "onderwerp": old_bericht.onderwerp,
                    "publicatiedatum": old_bericht.publicatiedatum.isoformat(),
                    "ontvanger": old_bericht.ontvanger,
                },
            },
        )

    def test_check_future_publicatiedatum(self, mock_process_cloudevent):
        now = timezone.now()
        date_1 = now + timedelta(days=1)
        date_10 = now + timedelta(days=10)

        BerichtFactory.create(publicatiedatum=date_1)
        BerichtFactory.create(publicatiedatum=date_10)

        with self.captureOnCommitCallbacks(execute=True):
            send_published_berichten()

        mock_process_cloudevent.assert_not_called()

        with freeze_time((date_1 + timedelta(days=1)).isoformat()):
            with self.captureOnCommitCallbacks(execute=True):
                send_published_berichten()

        assert mock_process_cloudevent.call_count == 1

        with freeze_time((date_10 + timedelta(days=1)).isoformat()):
            with self.captureOnCommitCallbacks(execute=True):
                send_published_berichten()

        assert mock_process_cloudevent.call_count == 2

    @patch(
        "openvtb.components.berichten.tasks.send_bericht_cloudevent",
        side_effect=Exception,
    )
    def test_does_not_publish_if_event_fails(self, m, mock_send):
        bericht = BerichtFactory.create(
            publicatiedatum=timezone.now() - timedelta(days=1),
            is_gepubliceerd=False,
        )

        with self.assertRaises(Exception):
            send_published_berichten()

        bericht.refresh_from_db()

        self.assertFalse(bericht.is_gepubliceerd)
