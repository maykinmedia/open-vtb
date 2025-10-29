from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusTaak(models.TextChoices):
    OPEN = "open", _("Open")
    UITGEVOERD = "uitgevoerd", _("Uitgevoerd")
    NIET_UITGEVOERD = "niet_uitgevoerd", _("Niet uitgevoerd")
    AFGEBROKEN = "afgebroken", _("Afgebroken")
    VERWERKT = "verwerkt", _("Verwerkt")
