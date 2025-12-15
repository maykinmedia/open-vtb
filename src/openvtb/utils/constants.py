from django.db import models
from django.utils.translation import gettext_lazy as _


class Valuta(models.TextChoices):
    EUR = "EUR", _("Euro")
