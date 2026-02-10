from django.conf import settings
from django.utils.translation import gettext_lazy as _

from openvtb.components.utils.drf_spectacular import URN_DESCRIPTION

custom_settings = {
    "TITLE": "Berichten API",
    "DESCRIPTION": _(
        "De berichten-service bestaat uit een beschrijving van afspraken, standaarden en referentiecomponenten "
        "aangevuld met interactiepatronen, ontwerpbesluiten en aanbevelingen. "
        "Het Berichten-patroon biedt een gestandaardiseerde, flexibele oplossing voor de communicatie tussen inwoners, "
        "ondernemers en gemeenten via digitale kanalen. Met dit patroon kunnen berichten eenvoudig geregistreerd worden en "
        "door verschillende applicaties worden opgehaald, weergegeven en verwerkt. "
        "In tegenstelling tot traditionele berichtgevingen (zoals e-mail), zijn berichten centraal geregistreerd "
        "en kunnen ze eenvoudig getoond en gerelateerd worden naast zaken, taken of producten binnen het gemeentelijke landschap. "
    )
    + URN_DESCRIPTION,
    "VERSION": settings.BERICHTEN_API_VERSION,
    "SERVERS": [{"url": "/berichten/api/v1"}],
    "TAGS": [
        {"name": "berichten"},
    ],
}
