from jsonschema import Draft202012Validator

ADRES_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "woonplaats": {"type": "string"},
        "postcode": {"type": "string"},
        "huisnummer": {"type": "string"},
        "huisletter": {"type": "string"},
        "huisnummertoevoeging": {"type": "string"},
        "buitenland": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "landcode": {"type": "string"},
                "landnaam": {"type": "string"},
                "adresregel1": {"type": "string"},
                "adresregel2": {"type": "string"},
                "adresregel3": {"type": "string"},
            },
        },
    },
}

AUTHENTIEKE_VERWIJZING = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "authentiekeVerwijzing",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "urn": {
            "type": "string",
            "pattern": "^urn:.*$",
        },
    },
    "required": [
        "urn",
    ],
}

NIET_AUTHENTIEKE_PERSOONSGEGEVENS = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "nietAuthentiekePersoonsgegevens",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "voornaam": {"type": "string"},
        "achternaam": {"type": "string"},
        "geboortedatum": {"type": "string", "format": "date"},
        "emailadres": {"type": "string", "format": "email"},
        "telefoonnummer": {"type": "string"},
        "postadres": ADRES_SCHEMA,
        "verblijfsadres": ADRES_SCHEMA,
    },
    "required": [
        "voornaam",
        "achternaam",
        "geboortedatum",
        "emailadres",
        "telefoonnummer",
    ],
}


NIET_AUTHENTIEKE_ORGANISATIEGEGEVENS = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "nietAuthentiekeOrganisatiegegevens",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "statutaireNaam": {"type": "string"},
        "bezoekadres": ADRES_SCHEMA,
        "postadres": ADRES_SCHEMA,
        "emailadres": {"type": "string", "format": "email"},
        "telefoonnummer": {"type": "string"},
    },
    "required": [
        "statutaireNaam",
        "emailadres",
        "telefoonnummer",
    ],
}


IS_INGEDIEND_DOOR_SCHEMA = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "isIngediendDoorSchema",
    "oneOf": [
        {
            "type": "object",
            "properties": {"authentiekeVerwijzing": AUTHENTIEKE_VERWIJZING},
            "required": ["authentiekeVerwijzing"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {
                "nietAuthentiekePersoonsgegevens": NIET_AUTHENTIEKE_PERSOONSGEGEVENS
            },
            "required": ["nietAuthentiekePersoonsgegevens"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {
                "nietAuthentiekeOrganisatiegegevens": NIET_AUTHENTIEKE_ORGANISATIEGEGEVENS
            },
            "required": ["nietAuthentiekeOrganisatiegegevens"],
            "additionalProperties": False,
        },
    ],
}
