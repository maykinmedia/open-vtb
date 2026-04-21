from django.utils import timezone

import structlog

from openvtb.celery import app
from openvtb.utils.cloudevents import process_cloudevent

from .constants import BERICHT_GEPUBLICEERD
from .models import Bericht

logger = structlog.stdlib.get_logger(__name__)


@app.task(ignore_result=True)
def send_published_berichten():
    for bericht in Bericht.objects.filter(
        publicatiedatum__lte=timezone.now(),
        is_gepubliceerd=False,
    ):
        logger.info("bericht_published", uuid=str(bericht.uuid))

        process_cloudevent(
            type_event=BERICHT_GEPUBLICEERD,
            subject=str(bericht.uuid),
            data={
                "onderwerp": bericht.onderwerp,
                "publicatiedatum": bericht.publicatiedatum,
                "ontvanger": bericht.ontvanger,
            },
        )

        bericht.is_gepubliceerd = True
        bericht.save()
