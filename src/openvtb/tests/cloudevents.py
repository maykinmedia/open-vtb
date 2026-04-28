from unittest import TestCase
from unittest.mock import patch

from django.test import override_settings

import requests_mock
from freezegun import freeze_time
from notifications_api_common.models import NotificationsConfig
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
