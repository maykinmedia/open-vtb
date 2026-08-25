from unittest import TestCase
from unittest.mock import patch

from django.test import override_settings

import requests
import requests_mock
from freezegun import freeze_time
from notifications_api_common.autoretry import add_autoretry_behaviour
from notifications_api_common.models import NotificationsConfig
from notifications_api_common.tasks import CloudEventException, send_cloudevent
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

NOTIFICATIONS_SOURCE = "openvtb-test"
FROZEN_TIME_Z = "2026-01-01T00:00:00Z"


def mock_cloud_event_send(m: requests_mock.Mocker, **kwargs) -> None:
    mock_kwargs = (
        {
            "status_code": 201,
            "json": {"dummy": "json"},
            **kwargs,
        }
        if "exc" not in kwargs
        else kwargs
    )
    m.post("http://webhook.local/cloudevents", **mock_kwargs)


def _ensure_cloudevent_autoretry():
    """
    Fix: some interaction between tests strips the autoretry
    wrapper that notifications_api_common applies to send_cloudevent at
    import time (task.run reverts to the unwrapped original), causing
    exceptions to propagate raw instead of triggering task.retry(). Root
    cause not yet identified; re-apply the wrapper if missing, since
    add_autoretry_behaviour is idempotent (no-ops if already wrapped).
    """
    if not hasattr(send_cloudevent, "_orig_run"):
        add_autoretry_behaviour(
            send_cloudevent,
            autoretry_for=(CloudEventException, requests.RequestException),
            retry_jitter=False,
        )


class CloudEventSettingMixin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._freezer = freeze_time(FROZEN_TIME_Z)
        cls._freezer.start()

        cls._override = override_settings(NOTIFICATIONS_SOURCE=NOTIFICATIONS_SOURCE)
        cls._override.enable()

    def setUp(self):
        super().setUp()
        _ensure_cloudevent_autoretry()

        self.service = ServiceFactory.create(
            api_root="http://webhook.local",
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token foo",
        )

        self.notifications_config = NotificationsConfig(
            notification_delivery_max_retries=3, notifications_api_service=self.service
        )

        self._notifications_patcher = patch(
            "notifications_api_common.models.NotificationsConfig.get_solo",
            return_value=self.notifications_config,
        )
        self._notifications_patcher.start()
        self.addCleanup(self._notifications_patcher.stop)

        self._patcher = patch(
            "notifications_api_common.models.NotificationsConfig.get_solo",
            return_value=NotificationsConfig(notifications_api_service=self.service),
        )
        self.mock_get_solo = self._patcher.start()
        self.addCleanup(self._patcher.stop)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "_freezer"):
            cls._freezer.stop()
        if hasattr(cls, "_override"):
            cls._override.disable()
        super().tearDownClass()
