from django.db import models
from django.utils.translation import gettext_lazy as _


class VerzoekTypeVersionStatus(models.TextChoices):
    PUBLISHED = "published", _("Published")
    DRAFT = "draft", _("Draft")
    DEPRECATED = "deprecated", _("Deprecated")
