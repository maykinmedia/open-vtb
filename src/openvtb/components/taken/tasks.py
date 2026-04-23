from datetime import date

import structlog

from openvtb.celery import app

from .cloudevents import (
    EXTERNETAAK_HERINNERD,
    EXTERNETAAK_VERLOPEN,
    send_taak_cloudevent,
)
from .constants import StatusTaak
from .models import ExterneTaak

logger = structlog.stdlib.get_logger(__name__)


@app.task(ignore_result=True)
def send_taak_event() -> None:
    """
    Sends CloudEvents for OPEN tasks:
    - reminder event when reminder date is reached
    - expiration event when handling term has expired
    """

    today = date.today()

    open_taken = ExterneTaak.objects.filter(status=StatusTaak.OPEN)

    # reminder event
    reminder_taken = open_taken.filter(
        datum_herinnering__lte=today, is_herinnering_verzonden=False
    )

    for taak in reminder_taken:
        logger.info("taak_herinnerd", uuid=str(taak.uuid))

        send_taak_cloudevent(EXTERNETAAK_HERINNERD, taak)

        taak.is_herinnering_verzonden = True
        taak.save(update_fields=["is_herinnering_verzonden"])

    # expiration event
    expired_taken = open_taken.filter(
        einddatum_handelings_termijn__lte=today, is_handelings_termijn_verzonden=False
    )

    for taak in expired_taken:
        logger.info("taak_verlopen", uuid=str(taak.uuid))

        send_taak_cloudevent(EXTERNETAAK_VERLOPEN, taak)

        taak.is_handelings_termijn_verzonden = True
        taak.save(update_fields=["is_handelings_termijn_verzonden"])
