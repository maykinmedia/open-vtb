from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from openvtb.utils.validators import (
    URNValidator,
    validate_charfield_entry,
    validate_phone_number,
    validate_postal_code,
)


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
            "0999aa",
            "1000  aa",
            "1000 aaa",
            "1000aaa",
            "1111,aa",
            "1111,a",
            '1111"a',
            '1111"aa',
        ]
        for invalid_postal_code in invalid_postal_codes:
            self.assertRaisesMessage(
                ValidationError,
                _("Invalid postal code."),
                validate_postal_code,
                invalid_postal_code,
            )

        self.assertIsNone(validate_postal_code("1015CJ"))
        self.assertIsNone(validate_postal_code("1015 CJ"))
        self.assertIsNone(validate_postal_code("1015cj"))
        self.assertIsNone(validate_postal_code("1015 cj"))
        self.assertIsNone(validate_postal_code("1015Cj"))
        self.assertIsNone(validate_postal_code("1015 Cj"))
        self.assertIsNone(validate_postal_code("1015cJ"))
        self.assertIsNone(validate_postal_code("1015 cJ"))

    def test_validate_phone_number(self):
        invalid_phone_numbers = [
            "0695azerty",
            "azerty0545",
            "@4566544++8",
            "onetwothreefour",
        ]
        for invalid_phone_number in invalid_phone_numbers:
            self.assertRaisesMessage(
                ValidationError,
                _("Invalid mobile phonenumber."),
                validate_phone_number,
                invalid_phone_number,
            )

        self.assertEqual(validate_phone_number(" 0695959595"), " 0695959595")
        self.assertEqual(validate_phone_number("+33695959595"), "+33695959595")
        self.assertEqual(validate_phone_number("00695959595"), "00695959595")
        self.assertEqual(validate_phone_number("00-69-59-59-59-5"), "00-69-59-59-59-5")
        self.assertEqual(validate_phone_number("00 69 59 59 59 5"), "00 69 59 59 59 5")


class URNValidatorTests(TestCase):
    def setUp(self):
        self.validator = URNValidator()
        return super().setUp()

    def test_valid_urns(self):
        valid_urns = [
            "urn:isbn:9780143127796",
            "urn:uuid:123e4567-e89b-12d3-a456-426614174000",
            "urn:example:document/2025/12",
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
