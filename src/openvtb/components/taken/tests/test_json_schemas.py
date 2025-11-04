from django.core.exceptions import ValidationError
from django.test import TestCase

from ..constants import SoortTaak
from ..validators import validate_jsonschema
from .factories import ExterneTaakFactory


class ValidateJSONSchemaTestCase(TestCase):
    def test_invalid_key_schema(self):
        validate_jsonschema({}, "")
        validate_jsonschema({}, "test")
        validate_jsonschema({}, None)

    def test_invalid_data_schema(self):
        # data values
        data_values = ["", "test", [], 0, False, None]
        for data in data_values:
            with self.assertRaises(ValidationError) as error:
                validate_jsonschema(data, SoortTaak.BETAALTAAK.value)
            self.assertTrue("data" in error.exception.message_dict)

        # data exists but the key doesn't exist
        with self.assertRaises(ValidationError) as error:
            validate_jsonschema({"data": "test"}, None)

        self.assertEqual(
            error.exception.message_dict,
            {
                "taak_soort": [
                    "Dit veld is verplicht voordat u het veld 'data' kunt instellen"
                ]
            },
        )


class ValidateBetaalTaakSchemaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.externe_taak = ExterneTaakFactory.create(
            taak_soort=SoortTaak.BETAALTAAK.value
        )

    def test_valid_schema(self):
        # all data
        self.externe_taak.data = {
            "bedrag": 10.12,
            "valuta": "EUR",
            "transactieomschrijving": "test",
            "doelrekening": {
                "naam": "test",
                "iban": "iban-code-test",
            },
        }
        self.externe_taak.full_clean()
        self.externe_taak.save()

    def test_invalid_schema_required_fields(self):
        with self.subTest("'bedrag' field required"):
            self.externe_taak.data = {
                # "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'bedrag' is a required property"]},
            )

        with self.subTest("'valuta' field required"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                # "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'valuta' is a required property"]},
            )

        with self.subTest("'transactieomschrijving' field required"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                # "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'transactieomschrijving' is a required property"]},
            )

        with self.subTest("'doelrekening' field required"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test",
                # "doelrekening": {
                # "naam": "test",
                # "iban": "iban-code-test",
                # },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'doelrekening' is a required property"]},
            )

        with self.subTest("'doelrekening.naam' field required"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    # "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'naam' is a required property"]},
            )

        with self.subTest("'doelrekening.iban' field required"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    # "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'iban' is a required property"]},
            )

    def test_invalid_schema_check_type(self):
        with self.subTest("'bedrag' is not number"):
            self.externe_taak.data = {
                "bedrag": "10",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'10' is not of type 'number'"]},
            )

        with self.subTest("'valuta' choices"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "TEST",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'TEST' is not one of ['EUR']"]},
            )

        with self.subTest("'transactieomschrijving' is not string"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": 123,
                "doelrekening": {
                    "naam": "test",
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["123 is not of type 'string'"]},
            )

        with self.subTest("'transactieomschrijving' is not dict"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": "TEST",
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["'TEST' is not of type 'object'"]},
            )

        with self.subTest("'transactieomschrijving' is too long"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test" * 100,
                "doelrekening": "TEST",
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()

            self.assertTrue(
                "is too long" in error.exception.message_dict["data"][0],
            )

        with self.subTest("'naam' is not string"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": True,
                    "iban": "iban-code-test",
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["True is not of type 'string'"]},
            )

        with self.subTest("'iban' is not string"):
            self.externe_taak.data = {
                "bedrag": 10.12,
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": 123,
                },
            }
            with self.assertRaises(ValidationError) as error:
                self.externe_taak.full_clean()
                self.externe_taak.save()
            self.assertEqual(
                error.exception.message_dict,
                {"data": ["123 is not of type 'string'"]},
            )


class ValidateGegevensUitvraagTaakSchemaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.externe_taak = ExterneTaakFactory.create(
            taak_soort=SoortTaak.GEGEVENSUITVRAAGTAAK.value
        )

    def test_valid_schema(self):
        self.externe_taak.data = {
            "uitvraagLink": "http://example.com/",
        }
        self.externe_taak.full_clean()
        self.externe_taak.save()

        self.externe_taak.data = {
            "uitvraagLink": "http://example.com/",
            "ontvangenGegevens": {},
        }
        self.externe_taak.full_clean()
        self.externe_taak.save()

        self.externe_taak.data = {
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
        self.externe_taak.full_clean()
        self.externe_taak.save()

    def test_invalid_schema(self):
        with self.assertRaises(ValidationError) as error:
            self.externe_taak.data = {}
            self.externe_taak.full_clean()
            self.externe_taak.save()
        self.assertEqual(
            error.exception.message_dict,
            {"data": ["'uitvraagLink' is a required property"]},
        )

        with self.assertRaises(ValidationError) as error:
            self.externe_taak.data = {
                "uitvraagLink": "test",
                "ontvangenGegevens": {},
            }
            self.externe_taak.full_clean()
            self.externe_taak.save()
        self.assertEqual(
            error.exception.message_dict,
            {"data": ["'test' is not a 'uri'"]},
        )

        with self.assertRaises(ValidationError) as error:
            self.externe_taak.data = {
                "uitvraagLink": "http://example.com",
                "ontvangenGegevens": "http://example.com",
            }
            self.externe_taak.full_clean()
            self.externe_taak.save()
        self.assertEqual(
            error.exception.message_dict,
            {"data": ["'http://example.com' is not of type 'object'"]},
        )


class ValidateFormulierTaakSchemaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.externe_taak = ExterneTaakFactory.create(
            taak_soort=SoortTaak.FORMULIERTAAK.value
        )

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
        self.externe_taak.data = {
            "formulierDefinitie": example,
            "ontvangenGegevens": example,
        }
        self.externe_taak.full_clean()
        self.externe_taak.save()

    def test_invalid_schema(self):
        with self.assertRaises(ValidationError) as error:
            self.externe_taak.data = {}
            self.externe_taak.full_clean()
            self.externe_taak.save()
        self.assertEqual(
            error.exception.message_dict,
            {"data": ["'formulierDefinitie' is a required property"]},
        )

        with self.assertRaises(ValidationError) as error:
            self.externe_taak.data = {
                "formulierDefinitie": "example",
                "ontvangenGegevens": {},
            }
            self.externe_taak.full_clean()
            self.externe_taak.save()
        self.assertEqual(
            error.exception.message_dict,
            {"data": ["'example' is not of type 'object'"]},
        )
