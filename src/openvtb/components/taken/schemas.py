from django.utils.translation import gettext as _

from jsonschema import Draft7Validator, Draft202012Validator

from .constants import SoortTaak

BETAAL_SCHEMA = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "BetaalTaak",
    "description": _(
        "Schema voor de BetaalTaak, bevat informatie over betaling en rekening van de ontvanger.",
    ),
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "bedrag": {
            "type": "string",
            "format": "decimal",
        },
        "valuta": {
            #  ISO 4217
            "type": "string",
            "default": "EUR",
            "enum": ["EUR"],
            "minLength": 3,
            "maxLength": 3,
            "pattern": "^[A-Z]{3}$",
        },
        "transactieomschrijving": {
            "type": "string",
            "maxLength": 80,
        },
        "doelrekening": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "naam": {
                    "type": "string",
                    "maxLength": 200,
                },
                "iban": {
                    "type": "string",
                    "format": "iban",
                },
            },
            "required": [
                "naam",
                "iban",
            ],
        },
    },
    "required": [
        "bedrag",
        "valuta",
        "transactieomschrijving",
        "doelrekening",
    ],
}

GEGEVENS_SCHEMA = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "GegevensUitvraagTaak",
    "description": _(
        "Schema voor de GegevensUitvraagTaak, inclusief links voor gegevensaanvragen en ontvangen gegevens."
    ),
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "uitvraagLink": {
            "type": "string",
            "format": "uri",
        },
        "ontvangenGegevens": {
            "type": "object",
            "title": "ontvangenGegevens",
            "description": _("Gegevens ontvangen als key-value"),
            "keys": {},
            "additionalProperties": True,
        },
    },
    "required": [
        "uitvraagLink",
    ],
}


FORMULIER_SCHEMA = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "FormulierTaak",
    "description": _(
        "Schema voor de FormulierTaak, inclusief definitie van het formulier en ontvangen gegevens."
    ),
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "formulierDefinitie": {
            "type": "object",
            "title": "formulierDefinitie",
            "description": _("JSON-structuur van het formulier (FormIO)"),
            "keys": {},
            "additionalProperties": True,
        },
        "ontvangenGegevens": {
            "type": "object",
            "title": "ontvangenGegevens",
            "description": _("Gegevens ontvangen als key-value"),
            "keys": {},
            "additionalProperties": True,
        },
    },
    "required": [
        "formulierDefinitie",
    ],
}

SCHEMA_MAPPING = {
    SoortTaak.BETAALTAAK: BETAAL_SCHEMA,
    SoortTaak.GEGEVENSUITVRAAGTAAK: GEGEVENS_SCHEMA,
    SoortTaak.FORMULIERTAAK: FORMULIER_SCHEMA,
}

FORMULIER_DEFINITIE_SCHEMA = {
    "$schema": Draft7Validator.META_SCHEMA["$id"],
    "title": "Formulier Schema",
    "type": "object",
    "properties": {
        "components": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "key": {"type": "string"},
                    "type": {"type": "string"},
                    "fileTypes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "string"},
                            },
                            "required": ["label", "value"],
                        },
                    },
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "string"},
                            },
                            "required": ["label", "value"],
                        },
                    },
                    "format": {"type": "string"},
                    "enableTime": {"type": "boolean"},
                    "decimalLimit": {"type": "number"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "values": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string"},
                                        "value": {"type": "string"},
                                    },
                                    "required": ["label", "value"],
                                },
                            }
                        },
                        "required": ["values"],
                    },
                },
                "required": ["label", "key", "type"],
            },
        }
    },
    "required": ["components"],
}
