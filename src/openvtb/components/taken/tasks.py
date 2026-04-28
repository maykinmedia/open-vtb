from datetime import date

import structlog
from celery import chord

from openvtb.celery import app

from .cloudevents import (
    EXTERNETAAK_HERINNERD,
    EXTERNETAAK_VERLOPEN,
    send_taak_cloudevent,
)
from .constants import StatusTaak
from .models import ExterneTaak

logger = structlog.stdlib.get_logger(__name__)


@app.task(bind=True)
def send_taak_reminder(self, taak_id: int) -> int:
    taak = ExterneTaak.objects.get(pk=taak_id)
    logger.info("taak_herinnerd", uuid=str(taak.uuid))
    send_taak_cloudevent(EXTERNETAAK_HERINNERD, taak)
    return taak_id


@app.task(bind=True)
def send_taak_expired(self, taak_id: int) -> int:
    taak = ExterneTaak.objects.get(pk=taak_id)
    logger.info("taak_verlopen", uuid=str(taak.uuid))
    send_taak_cloudevent(EXTERNETAAK_VERLOPEN, taak)
    return taak_id


@app.task
def mark_reminder_sent(taak_ids: list[int]) -> None:
    ExterneTaak.objects.filter(id__in=taak_ids).update(
        is_herinnering_verzonden=True,
    )


@app.task
def mark_expired_sent(taak_ids: list[int]) -> None:
    ExterneTaak.objects.filter(id__in=taak_ids).update(
        is_handelings_termijn_verzonden=True,
        status=StatusTaak.NIET_UITGEVOERD,
    )


@app.task(ignore_result=True)
def send_taak_events() -> None:
    """
    Sends CloudEvents for OPEN tasks:
    - reminder event when reminder_date is reached
    - expiration event when end_date has expired
    """
    today = date.today()
    open_taken = ExterneTaak.objects.filter(status=StatusTaak.OPEN)

    if not open_taken:
        logger.info("no_open_taken")
        return

    reminder_ids = list(
        open_taken.filter(
            datum_herinnering__lte=today, is_herinnering_verzonden=False
        ).values_list("id", flat=True)
    )

    if reminder_ids:
        header = [send_taak_reminder.s(tid) for tid in reminder_ids]
        chord(header)(mark_reminder_sent.s())

    expired_ids = list(
        open_taken.filter(
            einddatum_handelings_termijn__lte=today,
            is_handelings_termijn_verzonden=False,
        ).values_list("id", flat=True)
    )

    if expired_ids:
        header = [send_taak_expired.s(tid) for tid in expired_ids]
        chord(header)(mark_expired_sent.s())
