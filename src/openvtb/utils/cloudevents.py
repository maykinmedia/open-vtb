from django.conf import settings
from django.db import transaction

from notifications_api_common.cloudevents import (
    process_cloudevent as _process_cloudevent,
)


def process_cloudevent(
    type_event: str,
    subject: str | None = None,
    dataref: str | None = None,
    data: dict | None = None,
):
    if settings.ENABLE_CLOUD_EVENTS:
        transaction.on_commit(
            lambda: _process_cloudevent(type_event, subject, dataref, data)
        )
