from openvtb.utils.cloudevents import process_cloudevent

from .models import ExterneTaak

EXTERNETAAK_GEREGISTREERD = "nl.overheid.berichten.externetaak-geregistreerd"
EXTERNETAAK_HERINNERD = "nl.overheid.berichten.externetaak-herinnerd"
EXTERNETAAK_VERWERKT = "nl.overheid.berichten.externetaak-verwerkt"
EXTERNETAAK_UITGEVOERD = "nl.overheid.berichten.externetaak-uitgevoerd"
EXTERNETAAK_AFGEBROKEN = "nl.overheid.berichten.externetaak-afgebroken"
EXTERNETAAK_VERLOPEN = "nl.overheid.berichten.externetaak-verlopen"


def send_taak_cloudevent(type_event: str, taak: ExterneTaak) -> None:
    process_cloudevent(
        type_event=type_event,
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
