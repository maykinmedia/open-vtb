from django.db import models
from django.utils.translation import gettext_lazy as _


class HandelingsPerspectiefEnum(models.TextChoices):
    BETALEN = "betalen", _("Betalen")
    INCASSO = "incasso", _("Incasso")
    INFORMATIE_GEVEN = "informatie_geven", _("Informatie geven")
    INFORMATIE_KRIJGEN = "informatie_krijgen", _("Informatie krijgen")
    REACTIE_ONTVANGEN = "reactie_ontvangen", _("Reactie ontvangen")
    VERNIEUWING_NODIG = "vernieuwing_nodig", _("Vernieuwing nodig")
    UITNODIGING_VOOR_AFSPRAAK = (
        "uitnodiging_voor_afspraak",
        _("Uitnodiging voor afspraak"),
    )
