from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import CharField

from openvtb.utils.validators import validate_iban


@extend_schema_field({"type": "string", "example": "NL12BANK34567890"})
class IBANField(CharField):
    max_length = 34

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", self.max_length)
        super().__init__(**kwargs)
        self.validators.append(validate_iban)
