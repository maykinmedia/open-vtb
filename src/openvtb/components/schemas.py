from jsonschema import Draft202012Validator

# An array of objects, with 1 attribute: urn
IS_GERELATEERD_AAN_SCHEMA = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "isGerelateerdAanSchema",
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {"urn": {"type": "string", "pattern": "^urn:.*$"}},
        "required": ["urn"],
    },
}
