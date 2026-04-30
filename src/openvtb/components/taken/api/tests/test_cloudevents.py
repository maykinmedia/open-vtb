import datetime
from unittest.mock import patch

from django.test import override_settings

import requests_mock
from celery.exceptions import Retry
from freezegun import freeze_time
from notifications_api_common.tasks import send_cloudevent
from requests.exceptions import Timeout
from rest_framework import status
from vng_api_common.tests import reverse

from openvtb.components.taken.cloudevents import (
    EXTERNETAAK_AFGEBROKEN,
    EXTERNETAAK_GEREGISTREERD,
    EXTERNETAAK_UITGEVOERD,
    EXTERNETAAK_VERWERKT,
)
from openvtb.components.taken.constants import SoortTaak, StatusTaak
from openvtb.components.taken.tests.factories import ExterneTaakFactory
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
class ExterneTaakCloudEventTest(APITestCase):
    url = reverse("taken:externetaak-list")
    data = {
        "titel": "titel",
        "verwerkerTaakId": "123456",
        "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
        "taakSoort": SoortTaak.BETAALTAAK.value,
        "details": {
            "bedrag": "11",
            "transactieomschrijving": "test",
            "doelrekening": {
                "naam": "test",
                "code": "123-ABC",
                "iban": "NL12BANK34567890",
            },
        },
        "isToegewezenAan": "urn:example:12345",
    }

    @override_settings(ENABLE_CLOUD_EVENTS=False)
    def test_no_cloudevent_when_disabled(self, mock_process_cloudevent):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_process_cloudevent.assert_not_called()

    def test_taak_geregistreerd_cloudevent(self, mock_process_cloudevent):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_process_cloudevent.assert_called_once()

        taak_uuid = response.data["uuid"]
        payload = mock_process_cloudevent.call_args[0][0]
        self.assertEqual(
            payload,
            {
                "id": MOCKED_CLOUDEVENT_ID,
                "source": NOTIFICATIONS_SOURCE,
                "specversion": "1.0",
                "type": EXTERNETAAK_GEREGISTREERD,
                "subject": taak_uuid,
                "time": FROZEN_TIME_Z,
                "dataref": None,
                "datacontenttype": "application/json",
                "data": {
                    "taakSoort": response.json()["taakSoort"],
                    "titel": response.json()["titel"],
                    "status": response.json()["status"],
                    "einddatumHandelingsTermijn": response.json()[
                        "einddatumHandelingsTermijn"
                    ].replace("Z", "+00:00"),
                },
            },
        )

        # test different soortTaak
        self.data.pop("taakSoort")

        # betaaltaak
        url = reverse("taken:betaaltaak-list")
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, self.data)

        assert mock_process_cloudevent.call_count == 2

        # formuliertaak
        url = reverse("taken:formuliertaak-list")
        self.data["details"] = {
            "formulierDefinitie": {
                "key1": "value1",
                "components": [
                    {"type": "button", "label": "Submit", "key": "submit"},
                ],
            },
        }
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, self.data)

        assert mock_process_cloudevent.call_count == 3

        # urltaak
        url = reverse("taken:urltaak-list")
        self.data["details"] = {
            "uitvraagLink": "http://example.com/",
            "voorinvullenGegevens": {},
        }
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, self.data)

        assert mock_process_cloudevent.call_count == 4

    def test_multiple_taken_trigger_cloudevents(self, mock_process_cloudevent):
        for _ in range(3):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(self.url, self.data)
            assert response.status_code == status.HTTP_201_CREATED

        assert mock_process_cloudevent.call_count == 3

    def test_taak_update_status_cloudevent(self, mock_process_cloudevent):
        formuliertaak = ExterneTaakFactory.create(formuliertaak=True)
        formuliertaak_url = reverse(
            "taken:formuliertaak-detail", kwargs={"uuid": str(formuliertaak.uuid)}
        )
        externetaak = ExterneTaakFactory.create(formuliertaak=True)
        externetaak_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(externetaak.uuid)}
        )
        for taak, detail_url in [
            (formuliertaak, formuliertaak_url),
            (externetaak, externetaak_url),
        ]:
            # no status updates
            self.assertEqual(taak.status, StatusTaak.OPEN)
            response = self.client.patch(detail_url, {"titel": "new_title"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            taak.refresh_from_db()
            self.assertEqual(taak.titel, "new_title")
            self.assertEqual(taak.status, StatusTaak.OPEN)
            mock_process_cloudevent.assert_not_called()

            # OPEN -> UITGEVOERD
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.patch(
                    detail_url, {"status": StatusTaak.UITGEVOERD}
                )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            taak.refresh_from_db()
            self.assertEqual(taak.status, StatusTaak.UITGEVOERD)
            self.assertTrue(mock_process_cloudevent.called)  # send event
            mock_process_cloudevent.assert_called_once()
            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_UITGEVOERD)
            mock_process_cloudevent.reset_mock()

            # OPEN -> VERWERKT
            taak.status = StatusTaak.OPEN
            taak.save()
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.patch(
                    detail_url, {"status": StatusTaak.VERWERKT}
                )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            taak.refresh_from_db()
            self.assertEqual(taak.status, StatusTaak.VERWERKT)
            self.assertTrue(mock_process_cloudevent.called)  # send event
            mock_process_cloudevent.assert_called_once()
            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_VERWERKT)
            mock_process_cloudevent.reset_mock()

            # VERWERKT -> AFGEBROKEN
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.patch(
                    detail_url, {"status": StatusTaak.AFGEBROKEN}
                )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            taak.refresh_from_db()
            self.assertEqual(taak.status, StatusTaak.AFGEBROKEN)
            self.assertTrue(mock_process_cloudevent.called)  # send event
            mock_process_cloudevent.assert_called_once()
            payload = mock_process_cloudevent.call_args[0][0]
            self.assertEqual(payload["type"], EXTERNETAAK_AFGEBROKEN)
            mock_process_cloudevent.reset_mock()


@requests_mock.Mocker()
@freeze_time(FROZEN_TIME)
@patch("notifications_api_common.tasks.send_cloudevent.delay")
@patch("notifications_api_common.tasks.send_cloudevent.retry", side_effect=Retry)
@patch("notifications_api_common.cloudevents.uuid.uuid4", lambda: MOCKED_CLOUDEVENT_ID)
@override_settings(SITE_DOMAIN="testserver")
class CloudEventCeleryRetryTestCase(CloudEventSettingMixin, APITestCase):
    url = reverse("taken:externetaak-list")
    data = {
        "titel": "titel",
        "verwerkerTaakId": "123456",
        "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
        "taakSoort": SoortTaak.BETAALTAAK.value,
        "details": {
            "bedrag": "11",
            "transactieomschrijving": "test",
            "doelrekening": {
                "naam": "test",
                "code": "123-ABC",
                "iban": "NL12BANK34567890",
            },
        },
        "isToegewezenAan": "urn:example:12345",
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
        mock_send.assert_called_once()

        taak_uuid = response.data["uuid"]
        payload = mock_send.call_args[0][0]
        expected_payload = {
            "id": MOCKED_CLOUDEVENT_ID,
            "source": NOTIFICATIONS_SOURCE,
            "specversion": "1.0",
            "type": EXTERNETAAK_GEREGISTREERD,
            "subject": taak_uuid,
            "time": FROZEN_TIME_Z,
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "taakSoort": response.json()["taakSoort"],
                "titel": response.json()["titel"],
                "status": response.json()["status"],
                "einddatumHandelingsTermijn": response.json()[
                    "einddatumHandelingsTermijn"
                ].replace("Z", "+00:00"),
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
        mock_send.assert_called_once()

        taak_uuid = response.data["uuid"]
        payload = mock_send.call_args[0][0]
        expected_payload = {
            "id": MOCKED_CLOUDEVENT_ID,
            "source": NOTIFICATIONS_SOURCE,
            "specversion": "1.0",
            "type": EXTERNETAAK_GEREGISTREERD,
            "subject": taak_uuid,
            "time": FROZEN_TIME_Z,
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "taakSoort": response.json()["taakSoort"],
                "titel": response.json()["titel"],
                "status": response.json()["status"],
                "einddatumHandelingsTermijn": response.json()[
                    "einddatumHandelingsTermijn"
                ].replace("Z", "+00:00"),
            },
        }

        self.assertEqual(payload, expected_payload)

        # 2. check that if task is failed, celery retry is called
        mock_cloud_event_send(m, exc=Timeout)

        with self.assertRaises(Retry):
            send_cloudevent(expected_payload)

        retry_mock.assert_called_once()
