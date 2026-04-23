from datetime import date

import structlog

from openvtb.celery import app

from .cloudevents import EXTERNETAAK_HERINNERD, send_taak_cloudevent
from .constants import StatusTaak
from .models import ExterneTaak

logger = structlog.stdlib.get_logger(__name__)


@app.task(ignore_result=True)
def send_taak_event() -> None:
    """
    Sends reminder CloudEvents for OPEN external tasks whose reminder date has been reached.

    Processes all eligible tasks and marks them as reminded after execution.
    """
    for taak in ExterneTaak.objects.filter(
        datum_herinnering__lte=date.today(),
        is_herinnering_verzonden=False,
        status=StatusTaak.OPEN,
    ):
        logger.info("taak_herinnerd", uuid=str(taak.uuid))

        send_taak_cloudevent(EXTERNETAAK_HERINNERD, taak)

        taak.is_herinnering_verzonden = True
        taak.save()
