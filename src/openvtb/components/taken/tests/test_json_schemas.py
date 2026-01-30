from django.core.exceptions import ValidationError
from django.test import TestCase

from openvtb.utils.validators import validate_jsonschema

from ..constants import SoortTaak
from ..utils import get_json_schema


class ValidateJSONSchemaTestCase(TestCase):
    def test_invalid_key_schema(self):
        for key in ["", "test", None]:
            with self.assertRaises(ValidationError):
                validate_jsonschema(instance={}, schema=get_json_schema(key))

    def test_invalid_data_schema(self):
        # data values
        for instance in ["", "test", [], 0, False, None]:
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(
                    instance=instance,
                    schema=get_json_schema(SoortTaak.BETAALTAAK.value),
                )
            self.assertTrue("instance" in error.exception.message_dict)


class ValidateBetaalTaakSchemaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.taak_soort = SoortTaak.BETAALTAAK.value
        self.json_schema = get_json_schema(self.taak_soort)

    def test_valid_schema(self):
        # all data
        instance = {
            "bedrag": "10.12",
            "valuta": "EUR",
            "transactieomschrijving": "test",
            "doelrekening": {
                "naam": "test",
                "code": "123-ABC",
                "iban": "NL18BANK23481326",
            },
        }
        validate_jsonschema(instance=instance, schema=self.json_schema)

    def test_invalid_schema_required_fields(self):
        with self.subTest("'bedrag' field required"):
            instance = {
                # "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)

            self.assertEqual(
                error.exception.message_dict,
                {"instance": ["'bedrag' is a required property"]},
            )

        with self.subTest("'transactieomschrijving' field required"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                # "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance": ["'transactieomschrijving' is a required property"]},
            )

        with self.subTest("'doelrekening' field required"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                # "doelrekening": {
                # "naam": "test",
                # "code": "123-ABC",
                # "iban": "NL18BANK23481326",
                # },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance": ["'doelrekening' is a required property"]},
            )

        with self.subTest("'doelrekening.naam' field required"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    # "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.doelrekening": ["'naam' is a required property"]},
            )

        with self.subTest("'doelrekening.iban' field required"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    # "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.doelrekening": ["'iban' is a required property"]},
            )

    def test_invalid_schema_check_type(self):
        with self.subTest("'bedrag' is not decimal"):
            instance = {
                "bedrag": "test",  # not decimal
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.bedrag": ["'test' is not a valid decimal number"]},
            )
        with self.subTest("'bedrag'  has more than 2 decimal places"):
            instance = {
                "bedrag": "10.111",  # 3 decimals
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.bedrag": ["'10.111' has more than 2 decimal places"]},
            )

        with self.subTest("'valuta' choices"):
            instance = {
                "bedrag": "10.12",
                "valuta": "TEST",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.valuta": ["'TEST' is not one of ['EUR']"]},
            )

        with self.subTest("'transactieomschrijving' is not string"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": 123,
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.transactieomschrijving": ["123 is not of type 'string'"]},
            )

        with self.subTest("'doelrekening' is not dict"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": "TEST",
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.doelrekening": ["'TEST' is not of type 'object'"]},
            )

        with self.subTest("'transactieomschrijving' is too long"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test" * 100,
                "doelrekening": "TEST",
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertTrue(
                "is too long"
                in error.exception.message_dict["instance.transactieomschrijving"][0],
            )

        with self.subTest("'naam' is not string"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": True,
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.doelrekening.naam": ["True is not of type 'string'"]},
            )

        with self.subTest("'iban' is not string"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": 123,
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.doelrekening.iban": ["123 is not of type 'string'"]},
            )
        with self.subTest("'doelrekening.iban' field format"):
            instance = {
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "wrong-format",
                },
            }
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(instance=instance, schema=self.json_schema)
            self.assertEqual(
                error.exception.message_dict,
                {"instance.doelrekening.iban": ["'wrong-format' is not a valid IBAN"]},
            )


class ValidateGegevensUitvraagTaakSchemaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.taak_soort = SoortTaak.GEGEVENSUITVRAAGTAAK.value
        self.json_schema = get_json_schema(self.taak_soort)

    def test_valid_schema(self):
        instance = {
            "uitvraagLink": "http://example.com/",
        }
        validate_jsonschema(instance=instance, schema=self.json_schema)

        instance = {
            "uitvraagLink": "http://example.com/",
            "ontvangenGegevens": {},
        }
        validate_jsonschema(instance=instance, schema=self.json_schema)

        instance = {
            "uitvraagLink": "http://example.com/",
            "ontvangenGegevens": {
                "string": "hello world",  # string
                "integer": 42,  # integer
                "float": 3.14159,  # floating-point number
                "boolean_true": True,  # boolean True
                "null_value": None,  # null value (None in Python / null in JSON)
                "list_empty": [],  # empty list
                "list_numbers": [1, 2, 3],  # list of numbers
                "list_mixed": [1, "two", True, None],  # mixed list
                "list_nested": [[1, 2], ["a", "b"]],  # list of lists
                "dict_empty": {},  # empty dictionary
                "dict_nested": {  # nested dictionary
                    "nested_key1": "nested_value",
                    "nested_key2": 123,
                    "nested_key3": {
                        "key": 1,
                    },
                },
                "url": "http://example.com",  # string representing a URL
                "email": "user@example.com",  # string representing an email
                "date": "2025-11-03",  # string representing a date
                "datetime": "2025-11-03T12:34:56Z",  # string representing ISO8601 datetime
                "bytes_example": "SGVsbG8=",  # bytes encoded as base64 string
            },
        }
        validate_jsonschema(instance=instance, schema=self.json_schema)

    def test_invalid_schema(self):
        with self.assertRaises(ValidationError) as error:
            instance = {
                "uitvraagLink": "test",
                "ontvangenGegevens": {},
            }
            validate_jsonschema(instance=instance, schema=self.json_schema)
        self.assertEqual(
            error.exception.message_dict,
            {"instance.uitvraagLink": ["'test' is not a 'uri'"]},
        )

        with self.assertRaises(ValidationError) as error:
            instance = {
                "uitvraagLink": "http://example.com",
                "ontvangenGegevens": "http://example.com",
            }
            validate_jsonschema(instance=instance, schema=self.json_schema)
        self.assertEqual(
            error.exception.message_dict,
            {
                "instance.ontvangenGegevens": [
                    "'http://example.com' is not of type 'object'"
                ]
            },
        )


class ValidateFormulierTaakSchemaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.taak_soort = SoortTaak.FORMULIERTAAK.value
        self.json_schema = get_json_schema(self.taak_soort)

    def test_valid_schema(self):
        example = {
            "string": "hello world",  # string
            "integer": 42,  # integer
            "float": 3.14159,  # floating-point number
            "boolean_true": True,  # boolean True
            "null_value": None,  # null value (None in Python / null in JSON)
            "list_empty": [],  # empty list
            "list_numbers": [1, 2, 3],  # list of numbers
            "list_mixed": [1, "two", True, None],  # mixed list
            "list_nested": [[1, 2], ["a", "b"]],  # list of lists
            "dict_empty": {},  # empty dictionary
            "dict_nested": {  # nested dictionary
                "nested_key1": "nested_value",
                "nested_key2": 123,
                "nested_key3": {
                    "key": 1,
                },
            },
            "url": "http://example.com",  # string representing a URL
            "email": "user@example.com",  # string representing an email
            "date": "2025-11-03",  # string representing a date
            "datetime": "2025-11-03T12:34:56Z",  # string representing ISO8601 datetime
            "bytes_example": "SGVsbG8=",  # bytes encoded as base64 string
        }
        instance = {
            "formulierDefinitie": example,
            "ontvangenGegevens": example,
        }
        validate_jsonschema(instance=instance, schema=self.json_schema)

    def test_invalid_schema(self):
        with self.assertRaises(ValidationError) as error:
            instance = {
                "formulierDefinitie": "example",
                "ontvangenGegevens": {},
            }
            validate_jsonschema(instance=instance, schema=self.json_schema)
        self.assertEqual(
            error.exception.message_dict,
            {"instance.formulierDefinitie": ["'example' is not of type 'object'"]},
        )
