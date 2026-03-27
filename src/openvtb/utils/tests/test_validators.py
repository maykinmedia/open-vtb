from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from jsonschema import FormatError

from openvtb.utils.validators import (
    URNValidator,
    is_valid_color,
    is_valid_decimal,
    is_valid_email,
    is_valid_iban,
    validate_charfield_entry,
    validate_iban,
    validate_jsonschema,
    validate_phone_number,
    validate_postal_code,
)

SCHEMA_ALL_FORMATS = {
    "type": "object",
    "properties": {
        "color": {"type": "string", "format": "color"},
        "date": {"type": "string", "format": "date"},
        "date-time": {"type": "string", "format": "date-time"},
        "duration": {"type": "string", "format": "duration"},
        "email": {"type": "string", "format": "email"},
        "hostname": {"type": "string", "format": "hostname"},
        "idn-hostname": {"type": "string", "format": "idn-hostname"},
        "ipv4": {"type": "string", "format": "ipv4"},
        "ipv6": {"type": "string", "format": "ipv6"},
        "iri": {"type": "string", "format": "iri"},
        "iri-reference": {"type": "string", "format": "iri-reference"},
        "json-pointer": {"type": "string", "format": "json-pointer"},
        "regex": {"type": "string", "format": "regex"},
        "relative-json-pointer": {"type": "string", "format": "relative-json-pointer"},
        "time": {"type": "string", "format": "time"},
        "uri": {"type": "string", "format": "uri"},
        "uri-reference": {"type": "string", "format": "uri-reference"},
        "uri-template": {"type": "string", "format": "uri-template"},
        "uuid": {"type": "string", "format": "uuid"},
    },
}


class ValidatorsTestCase(TestCase):
    """
    Validates the functions defined in ``utils.validators`` module.
    """

    def test_validate_charfield_entry_apostrophe_not_allowed(self):
        """
        Tests the ``validate_charfield_entry`` function when not explicitly
        allowing apostrophe character.
        """
        self.assertRaisesMessage(
            ValidationError,
            _("The provided value contains an invalid character: %s") % "'",
            validate_charfield_entry,
            "let's fail",
        )

    def test_validate_charfield_entry_apostrophe_allowed(self):
        """
        Tests the ``validate_charfield_entry`` function when explicitly
        allowing apostrophe character.
        """
        self.assertEqual(
            validate_charfield_entry("let's pass", allow_apostrophe=True), "let's pass"
        )

    def test_validate_postal_code(self):
        """
        Test all valid postal code and also test invalid values
        """
        invalid_postal_codes = [
            "0000AA",
            "0999AA",
            "1000  AA",
            "1000 AAA",
            "1000AAA",
            "0000aa",
            "0000 aa",
            "0999aa",
            "1000  aa",
            "1000 aaa",
            "1000aaa",
            "1111,aa",
            "1111,a",
            '1111"a',
            '1111"aa',
            "1111 Aa",
            "1111 aA",
            "1015CJ",
        ]
        for invalid_postal_code in invalid_postal_codes:
            self.assertRaisesMessage(
                ValidationError,
                "Postcode moet aan het volgende formaat voldoen: `1234 AB` (met spatie)",
                validate_postal_code,
                invalid_postal_code,
            )
        self.assertIsNone(validate_postal_code("1015 CJ"))

    def test_validate_phone_number(self):
        valid_phone_numbers = [
            "0612345678",
            "0201234567",
            "+31612345678",
            "+441134960000",
            "+12065550100",
            "0031612345678",
            "00311234567",
        ]
        invalid_phone_numbers = [
            "0800123456",
            "0900123456",
            "0881234567",
            "1400",
            "14012",
            "14079",
            "0695azerty",
            "azerty0545",
            "@4566544++8",
            "onetwothreefour",
            "020 753 0523",
            "+311234",
            "316123456789",
        ]
        for invalid_phone_number in invalid_phone_numbers:
            with self.subTest(invalid_phone_number):
                self.assertRaisesMessage(
                    ValidationError,
                    "Het opgegeven telefoonnummer is ongeldig",
                    validate_phone_number,
                    invalid_phone_number,
                )

        for valid_phone_number in valid_phone_numbers:
            with self.subTest(valid_phone_number):
                validate_phone_number(valid_phone_number)

    def test_validate_iban(self):
        invalid_ibans = [
            "1231md4832842834",
            "jda42034nnndnd23923",
            "AB123dasd#asdasda",
            "AB12",
            "AB1259345934953495934953495345345345",
        ]
        for iban in invalid_ibans:
            self.assertRaisesMessage(
                ValidationError,
                "Ongeldige IBAN",
                validate_iban,
                iban,
            )
            with self.assertRaises(FormatError):
                is_valid_iban(iban)  # format checker function

        valid_ibans = [
            "NL91ABNA0417164300",
            "DE89370400440532013000",
            "FR1420041010050500013M02606",
            "GB82WEST12345698765432",
            "AB12TEST1253678",
            "AB12test1253678",
            "ab1299999999999",
            "ab129",
            "ab12aaaaaaaaaa",
        ]
        for iban in valid_ibans:
            self.assertIsNone(validate_iban(iban))
            self.assertTrue(is_valid_iban(iban))  # format checker function

    def test_decimal(self):
        invalid_decimals = ["test", "123test", "123,15", "###", None]
        for decimal in invalid_decimals:
            with self.assertRaises(FormatError):
                is_valid_decimal(decimal)

        valid_decimals = ["123", "123.15", 123]
        for decimal in valid_decimals:
            self.assertTrue(is_valid_decimal(decimal))

    def test_email(self):
        invalid_emails = [
            "test",
            "@missingusername.com",
            "username@.com",
            "user@site..com",
            "user@com",
            "user@site,com",
            None,
            123,
        ]
        for email in invalid_emails:
            self.assertFalse(is_valid_email(email))

        valid_emails = [
            "user@example.com",
            "user.name+tag@example.co.uk",
            "user_name-test@example.com",
            "user!?name@example.io",
            "user123@example123.com",
        ]
        for email in valid_emails:
            self.assertTrue(is_valid_email(email))

    def test_color(self):
        invalid_colors = ["notacolor", "123456", "#12345G"]
        for color in invalid_colors:
            with self.assertRaises(FormatError):
                is_valid_color(color)

        valid_colors = ["red", "#fff", "#FFFFFF"]
        for color in valid_colors:
            self.assertTrue(is_valid_color(color))


class URNValidatorTests(TestCase):
    def setUp(self):
        self.validator = URNValidator()
        return super().setUp()

    def test_valid_urns(self):
        valid_urns = [
            "urn:isbn:9780143127796",
            "urn:uuid:123e4567-e89b-12d3-a456-426614174000",
            "urn:example:document/2026/12",
            "urn:maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "urn:maykin:abc:ztc:zaak:abc:cde:123:456",
            "urn:isbn:abc%5E123",  # percent-encoded
            "urn:example-test:document@123",
            "urn:example:document-123.-_~",  # unreserved values
            "urn:example:document-123!$&'/*()+,;=",  # sub-delims values
            "urn:example:document:test@test",  # extra values
            "urn:example:document/123",
            "urn:example:document/123?+revision1",  # r_component
            "urn:example:document/123?=revision1",  # q_component
            "urn:example:document/123?+revision1?=query#section2",  # fragment
        ]

        for urn in valid_urns:
            self.validator(urn)

    def test_invalid_urns(self):
        invalid_urns = [
            # missing 'urn:' prefix
            "isbn:9780143127796",
            "uuid:123e4567-e89b-12d3-a456-426614174000",
            # invalid NID
            "urn:-isbn:9780143127796",  # starts with '-'
            "urn:isbn-:9780143127796",  # ends with '-'
            "urn:123456789012345678901234567890123:abc",  # >32 chars
            "urn:£$%:123",
            "urn:in valid:123",
            "urn:!invalid:123",
            # invalid characters in NSS
            "urn:uuid",
            "urn:isbn:",
            "urn:isbn:abc^123",
            "urn:example:doc name",
            "urn:example:test?123",
            # invalid
            "urn::123",
            "urn:abc",
            "urn:",
        ]

        for urn in invalid_urns:
            with self.assertRaises(ValidationError) as error:
                self.validator(urn)

            self.assertEqual(
                error.exception.message,
                "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            )


class JSONSchemaFormatTests(TestCase):
    def test_color(self):
        data = {}
        invalid_values = ["#12", "#12345", "#zzzzzz", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["color"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        validate_jsonschema({"color": "#ff0000"}, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"color": "red"}, SCHEMA_ALL_FORMATS)

    def test_date(self):
        data = {}
        invalid_values = ["2026-13-40", None, 123, "test"]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["date"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"date": "2026-01-01"}, SCHEMA_ALL_FORMATS)

    def test_date_time(self):
        data = {}
        invalid_values = ["2026-13-40T25:61:61Z", None, 123, "test"]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["date-time"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"date-time": "2026-01-01T12:34:56Z"}, SCHEMA_ALL_FORMATS)

    def test_duration(self):
        data = {}
        invalid_values = ["not-a-duration", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["duration"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"duration": "P3Y6M4DT12H30M5S"}, SCHEMA_ALL_FORMATS)

    def test_email(self):
        data = {}
        invalid_values = ["test", None, "123", 123, "test-test@.test"]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["email"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        validate_jsonschema({"email": "test@example.com"}, SCHEMA_ALL_FORMATS)

    def test_hostname(self):
        data = {}
        invalid_values = ["-invalid-host", "invalid_host", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["hostname"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"hostname": "example.com"}, SCHEMA_ALL_FORMATS)

    def test_idn_hostname(self):
        data = {}
        invalid_values = ["-invalid.com", "invalid-.com", "inv@lid.com", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["idn-hostname"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_values = ["münchen.com", "tęst.com", "crème.fr"]
        for val in valid_values:
            data["idn-hostname"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_ipv4(self):
        data = {}
        invalid_values = ["999.999.999.999", "abc.def.ghi.jkl", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["ipv4"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"ipv4": "192.168.1.1"}, SCHEMA_ALL_FORMATS)

    def test_ipv6(self):
        data = {}
        invalid_values = ["invalid:ipv6", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["ipv6"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema(
            {"ipv6": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}, SCHEMA_ALL_FORMATS
        )

    def test_iri(self):
        data = {}
        invalid_values = ["http://exa mple.com", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["iri"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_values = ["https://example.com", "https://münchen.com/über"]
        for val in valid_values:
            data["iri"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_iri_reference(self):
        data = {}
        invalid_refs = ["ht tp://example.com", "://missing.scheme.com", None, 123]
        for val in invalid_refs:
            with self.assertRaises(ValidationError):
                data["iri-reference"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_refs = ["/relative/path", "crème/cheese", "münchen/über"]
        for val in valid_refs:
            data["iri-reference"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_json_pointer(self):
        data = {}
        invalid_values = ["foo/bar", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["json-pointer"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"json-pointer": "/foo/bar"}, SCHEMA_ALL_FORMATS)

    def test_regex(self):
        data = {}
        invalid_values = ["[unclosed", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["regex"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"regex": "^[a-z]+$"}, SCHEMA_ALL_FORMATS)

    def test_relative_json_pointer(self):
        data = {}
        invalid_values = ["foo", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["relative-json-pointer"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"relative-json-pointer": "0/foo"}, SCHEMA_ALL_FORMATS)

    def test_time(self):
        data = {}
        invalid_values = ["25:61:61", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["time"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"time": "12:34:56Z"}, SCHEMA_ALL_FORMATS)

    def test_uri(self):
        data = {}
        invalid_values = ["not-a-uri", "://missing", None, 123]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["uri"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri": "https://example.com/path"}, SCHEMA_ALL_FORMATS)

    def test_uri_reference(self):
        data = {}
        invalid_values = [None, 123, "http://[invalid"]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["uri-reference"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri-reference": "/relative/path"}, SCHEMA_ALL_FORMATS)

    def test_uri_template(self):
        data = {}
        invalid_values = [None, 123, "{unclosed"]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["uri-template"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri-template": "/users/{id}"}, SCHEMA_ALL_FORMATS)

    def test_uuid(self):
        data = {}
        invalid_values = ["not-a-uuid", None, 123, "1234"]
        for val in invalid_values:
            with self.assertRaises(ValidationError):
                data["uuid"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema(
            {"uuid": "123e4567-e89b-12d3-a456-426614174000"}, SCHEMA_ALL_FORMATS
        )
