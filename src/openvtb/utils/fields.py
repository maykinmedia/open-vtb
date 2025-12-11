from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import URNValidator


class URNField(models.CharField):
    """
    A custom Django model field to store a valid URN (RFC 8141: Uniform Resource Names)
    https://datatracker.ietf.org/doc/html/rfc8141

    This field extends CharField and automatically validates the value
    against a basic URN pattern: `urn:<namespace>:<resource>`.
    """

    default_validators = [URNValidator()]
    description = _("URN")

    def __init__(self, *args, **kwargs):
        # Default max length 255 characters
        kwargs.setdefault("max_length", 255)
        super().__init__(*args, **kwargs)
