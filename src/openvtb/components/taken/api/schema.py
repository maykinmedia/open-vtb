from django.conf import settings

custom_settings = {
    "TITLE": "taken",
    "DESCRIPTION": "",
    "VERSION": settings.TAKEN_API_VERSION,
    "SERVERS": [{"url": "/taken/api/v1"}],
    "TAGS": [
        {"name": "externetaken"},
        {"name": "betaaltaken"},
        {"name": "gegevensuitvraagtaken"},
        {"name": "formuliertaken"},
    ],
}
