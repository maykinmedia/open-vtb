import json

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from openvtb.components.drf_spectacular import URN_DESCRIPTION
from openvtb.components.taken.schemas import FORMULIER_DEFINITIE_SCHEMA

FORMULIERTAKEN_DESCRIPTION = (
    "Het veld `formDefinition` bevat het JSON-schema dat de structuur van het formulier definieert "
    "dat bij de taak hoort. Het specificeert de beschikbare velden, hun gegevenstypen, validatieregels "
    "en welke eigenschappen verplicht zijn. "
    "Een JSON-schema om te valideren:\n\n```json\n"
    f"{json.dumps(FORMULIER_DEFINITIE_SCHEMA, indent=4)}\n```"
)

custom_settings = {
    "TITLE": "Taken API",
    "DESCRIPTION": _(
        "De 'Taken-Service' is een gestandaardiseerde architectuur voor Nederlandse overheidssystemen,"
        "ontworpen om acties (taken) te definiëren en te beheren die burgers moeten uitvoeren."
        "Het zorgt voor consistente communicatie tussen verschillende applicaties."
    )
    + URN_DESCRIPTION,
    "VERSION": settings.TAKEN_API_VERSION,
    "SERVERS": [{"url": "/taken/api/v1"}],
    "TAGS": [
        {"name": "externetaken"},
        {"name": "betaaltaken"},
        {"name": "urltaken"},
        {
            "name": "formuliertaken",
            "description": FORMULIERTAKEN_DESCRIPTION,
        },
    ],
}
