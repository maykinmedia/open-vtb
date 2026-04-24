from openvtb.utils.cloudevents import process_cloudevent

from .models import Bericht

BERICHT_GEREGISTREERD = "nl.overheid.berichten.bericht-geregistreerd"
BERICHT_GEPUBLICEERD = "nl.overheid.berichten.bericht-gepubliceerd"


def send_bericht_cloudevent(type_event: str, bericht: Bericht) -> None:
    process_cloudevent(
        type_event=type_event,
        subject=str(bericht.uuid),
        data={
            "onderwerp": bericht.onderwerp,
            "publicatiedatum": bericht.publicatiedatum.isoformat()
            if bericht.publicatiedatum
            else "",
            "ontvanger": bericht.ontvanger,
        },
    )
