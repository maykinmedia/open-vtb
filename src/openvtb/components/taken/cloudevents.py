from openvtb.utils.cloudevents import process_cloudevent

from .models import ExterneTaak

EXTERNETAAK_GEREGISTREERD = "nl.overheid.taken.externetaak-geregistreerd"
EXTERNETAAK_HERINNERD = "nl.overheid.taken.externetaak-herinnerd"
EXTERNETAAK_VERWERKT = "nl.overheid.taken.externetaak-verwerkt"
EXTERNETAAK_UITGEVOERD = "nl.overheid.taken.externetaak-uitgevoerd"
EXTERNETAAK_AFGEBROKEN = "nl.overheid.taken.externetaak-afgebroken"
EXTERNETAAK_VERLOPEN = "nl.overheid.taken.externetaak-verlopen"


def send_taak_cloudevent(type_event: str, taak: ExterneTaak) -> None:
    process_cloudevent(
        type_event=type_event,
        subject=str(taak.uuid),
        data={
            "taakSoort": taak.taak_soort,
            "titel": taak.titel,
            "status": taak.status,
            "einddatumHandelingsTermijn": taak.einddatum_handelings_termijn.isoformat()
            if taak.einddatum_handelings_termijn
            else "",
        },
    )
