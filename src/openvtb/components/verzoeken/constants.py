from django.db import models
from django.utils.translation import gettext_lazy as _


class VerzoekTypeVersionStatus(models.TextChoices):
    PUBLISHED = "published", _("Published")
    DRAFT = "draft", _("Draft")
    DEPRECATED = "deprecated", _("Deprecated")


class VerzoektypeOpvolging(models.TextChoices):
    NIET_TOT_ZAAK = "niet", _("Leidt niet tot een zaak")
    MOGELIJK_TOT_ZAAK = "mogelijk", _("Leidt mogelijk tot een zaak")
    ALTIJD_TOT_ZAAK = "altijd", _("Leidt altijd tot een zaak")
    MEERDERE_ZAKEN = "meerdere", _("Leidt altijd tot meerdere zaken")
