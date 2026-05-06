from unittest.mock import patch

from django.test import override_settings

import requests_mock
from celery.exceptions import Retry
from freezegun.api import freeze_time
from notifications_api_common.tasks import send_cloudevent
from requests.exceptions import Timeout
from rest_framework import status
from vng_api_common.tests import reverse

from openvtb.components.berichten.cloudevents import BERICHT_GEREGISTREERD
from openvtb.tests.cloudevents import CloudEventSettingMixin, mock_cloud_event_send
from openvtb.utils.api_testcase import APITestCase

MOCKED_CLOUDEVENT_ID = "f347fd1f-dac1-4870-9dd0-f6c00edf4bf7"
NOTIFICATIONS_SOURCE = "openvtb-test"
FROZEN_TIME = "2026-01-01"
FROZEN_TIME_Z = "2026-01-01T00:00:00Z"


@freeze_time(FROZEN_TIME)
@patch("notifications_api_common.tasks.send_cloudevent.delay")
@patch("notifications_api_common.cloudevents.uuid.uuid4", lambda: MOCKED_CLOUDEVENT_ID)
@override_settings(NOTIFICATIONS_SOURCE=NOTIFICATIONS_SOURCE)
class BerichtenCloudEventTest(APITestCase):
    maxDiff = None
    url = reverse("berichten:bericht-list")
    data = {
        "onderwerp": "onderwerp",
        "berichtTekst": "berichtTekst berichtTekst",
        "referentie": "referentie",
        "ontvanger": "urn:maykin:ontvanger:1234",
        "berichtType": "12345678",
        "mijnOverheidBerichtenbox": True,
    }

    @override_settings(ENABLE_CLOUD_EVENTS=False)
    def test_no_cloudevent_when_disabled(self, mock_process_cloudevent):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_process_cloudevent.assert_not_called()

    def test_bericht_geregistreerd_cloudevent(self, mock_process_cloudevent):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_process_cloudevent.assert_called_once()

        bericht_uuid = response.data["uuid"]
        payload = mock_process_cloudevent.call_args[0][0]

        self.assertEqual(
            payload,
            {
                "id": MOCKED_CLOUDEVENT_ID,
                "source": NOTIFICATIONS_SOURCE,
                "specversion": "1.0",
                "type": BERICHT_GEREGISTREERD,
                "subject": bericht_uuid,
                "time": FROZEN_TIME_Z,
                "dataref": None,
                "datacontenttype": "application/json",
                "data": {
                    "onderwerp": response.data["onderwerp"],
                    "publicatiedatum": response.data["publicatiedatum"].replace(
                        "Z", "+00:00"
                    ),
                    "ontvanger": response.data["ontvanger"],
                },
            },
        )

    def test_multiple_berichten_trigger_cloudevents(self, mock_process_cloudevent):
        for _ in range(3):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(self.url, self.data)
            assert response.status_code == status.HTTP_201_CREATED

        assert mock_process_cloudevent.call_count == 3


@requests_mock.Mocker()
@freeze_time(FROZEN_TIME)
@patch("notifications_api_common.tasks.send_cloudevent.delay")
@patch("notifications_api_common.tasks.send_cloudevent.retry", side_effect=Retry)
@patch("notifications_api_common.cloudevents.uuid.uuid4", lambda: MOCKED_CLOUDEVENT_ID)
@override_settings(SITE_DOMAIN="testserver")
class CloudEventCeleryRetryTestCase(CloudEventSettingMixin, APITestCase):
    url = reverse("berichten:bericht-list")
    data = {
        "onderwerp": "onderwerp",
        "berichtTekst": "berichtTekst berichtTekst",
        "referentie": "referentie",
        "ontvanger": "urn:maykin:ontvanger:1234",
        "berichtType": "12345678",
        "mijnOverheidBerichtenbox": True,
    }

    def test_cloud_event_client_error_retry(self, m, retry_mock, mock_send):
        """
        Verify that a retry is called when the sending of the notification didn't
        succeed due to an invalid response.
        """
        # 1. send event
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        bericht_uuid = response.data["uuid"]

        payload = mock_send.call_args[0][0]
        expected_payload = {
            "id": MOCKED_CLOUDEVENT_ID,
            "source": NOTIFICATIONS_SOURCE,
            "specversion": "1.0",
            "type": BERICHT_GEREGISTREERD,
            "subject": bericht_uuid,
            "time": FROZEN_TIME_Z,
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "onderwerp": response.data["onderwerp"],
                "publicatiedatum": response.data["publicatiedatum"].replace(
                    "Z", "+00:00"
                ),
                "ontvanger": response.data["ontvanger"],
            },
        }

        self.assertEqual(payload, expected_payload)

        # 2. check that if task is failed, celery retry is called
        mock_cloud_event_send(m, status_code=403)

        with self.assertRaises(Retry):
            send_cloudevent(expected_payload)

        retry_mock.assert_called_once()

    def test_cloud_event_timeout_retry(self, m, retry_mock, mock_send):
        """
        Verify that a retry is called when sending the notification times out.
        """

        # 1. send event
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        bericht_uuid = response.data["uuid"]

        payload = mock_send.call_args[0][0]
        expected_payload = {
            "id": MOCKED_CLOUDEVENT_ID,
            "source": NOTIFICATIONS_SOURCE,
            "specversion": "1.0",
            "type": BERICHT_GEREGISTREERD,
            "subject": bericht_uuid,
            "time": FROZEN_TIME_Z,
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "onderwerp": response.data["onderwerp"],
                "publicatiedatum": response.data["publicatiedatum"].replace(
                    "Z", "+00:00"
                ),
                "ontvanger": response.data["ontvanger"],
            },
        }

        self.assertEqual(payload, expected_payload)

        # 2. check that if task is failed, celery retry is called
        mock_cloud_event_send(m, exc=Timeout)

        with self.assertRaises(Retry):
            send_cloudevent(expected_payload)

        retry_mock.assert_called_once()
