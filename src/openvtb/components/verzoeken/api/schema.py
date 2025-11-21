from django.conf import settings
from django.utils.translation import gettext_lazy as _

custom_settings = {
    "TITLE": "Verzoeken API",
    "DESCRIPTION": _(
        """
        De 'Verzoeken-API' slaat ingediende formuliergegevens op als gestructureerde JSON.
        Aangezien formulieren elk type veld kunnen bevatten, definieert elk formulier een JSON-schema dat de verwachte structuur specificeert.
        Inkomende gegevens worden getoetst aan dit schema en opgeslagen in een consistent, gestructureerd formaat.
        """
    ),
    "VERSION": settings.TAKEN_API_VERSION,
    "SERVERS": [{"url": "/verzoeken/api/v1"}],
    "TAGS": [
        {"name": "verzoeken"},
    ],
}
