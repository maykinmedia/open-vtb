from django.utils import timezone

import structlog

from openvtb.celery import app

from .cloudevents import BERICHT_GEPUBLICEERD, send_bericht_cloudevent
from .models import Bericht

logger = structlog.stdlib.get_logger(__name__)


@app.task(ignore_result=True)
def send_published_berichten():
    for bericht in Bericht.objects.filter(
        publicatiedatum__lte=timezone.now(), is_gepubliceerd=False
    ).iterator():
        logger.info("bericht_published", uuid=str(bericht.uuid))

        send_bericht_cloudevent(BERICHT_GEPUBLICEERD, bericht)

        bericht.is_gepubliceerd = True
        bericht.save()
