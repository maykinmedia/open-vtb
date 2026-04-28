from django.utils import timezone

import structlog
from celery import chord

from openvtb.celery import app

from .cloudevents import BERICHT_GEPUBLICEERD, send_bericht_cloudevent
from .models import Bericht

logger = structlog.stdlib.get_logger(__name__)


@app.task(bind=True)
def send_bericht(self, bericht_id: int) -> int:
    """
    Sends published CloudEvent for a bericht.
    """
    bericht = Bericht.objects.get(pk=bericht_id)
    send_bericht_cloudevent(BERICHT_GEPUBLICEERD, bericht)
    logger.info("bericht_published", extra={"uuid": str(bericht.uuid)})
    return bericht_id


@app.task
def mark_as_published(bericht_ids: list[int]) -> None:
    """
    Marks berichten as published.
    """
    Bericht.objects.filter(id__in=bericht_ids).update(is_gepubliceerd=True)


@app.task
def send_published_berichten():
    """
    Publishes all Bericht instances whose publication date has been reached
    and which are not yet marked as published.

    NOTE:
    This implementation loads all matching IDs into memory and creates a Celery
    signature per item at once. If the dataset grows significantly, this may
    lead to memory pressure and large broker payloads. Consider batching or
    chunked processing for scalability.
    """
    bericht_ids = list(
        Bericht.objects.filter(
            publicatiedatum__lte=timezone.now(),
            is_gepubliceerd=False,
        ).values_list("id", flat=True)
    )

    if not bericht_ids:
        logger.info("no_berichten_to_publish")
        return

    header = [send_bericht.s(bericht_id) for bericht_id in bericht_ids]
    chord(header)(mark_as_published.s())
