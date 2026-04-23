from datetime import date

import structlog

from openvtb.celery import app
from openvtb.utils.cloudevents import process_cloudevent

from .constants import EXTERNETAAK_HERINNERD, StatusTaak
from .models import ExterneTaak

logger = structlog.stdlib.get_logger(__name__)


@app.task(ignore_result=True)
def send_taak_reminder() -> None:
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

        process_cloudevent(
            type_event=EXTERNETAAK_HERINNERD,
            subject=str(taak.uuid),
            data={
                "taak_soort": taak.taak_soort,
                "titel": taak.titel,
                "status": taak.status,
                "einddatumHandelingsTermijn": taak.einddatum_handelings_termijn.isoformat()
                if taak.einddatum_handelings_termijn
                else "",
            },
        )

        taak.is_herinnering_verzonden = True
        taak.save()
