from django.conf import settings
from django.utils.translation import gettext_lazy as _

custom_settings = {
    "TITLE": "Taken API",
    "DESCRIPTION": _(
        """
        De 'Taken-Service' is een gestandaardiseerde architectuur voor Nederlandse overheidssystemen,
        ontworpen om acties (taken) te definiëren en te beheren die burgers moeten uitvoeren.
        Het zorgt voor consistente communicatie tussen verschillende applicaties.
        """
    ),
    "VERSION": settings.TAKEN_API_VERSION,
    "SERVERS": [{"url": "/taken/api/v1"}],
    "TAGS": [
        {"name": "externetaken"},
        {"name": "betaaltaken"},
        {"name": "gegevensuitvraagtaken"},
        {"name": "formuliertaken"},
    ],
}
