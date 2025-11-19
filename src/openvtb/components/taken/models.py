import uuid as _uuid

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_jsonform.models.fields import JSONField

from openvtb.utils.validators import validate_date

from .constants import SoortTaak, StatusTaak


class ExterneTaak(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text=(
            "Een UUID waarmee een ZAC een link kan leggen tussen de taak en zijn eigen administratie."
        ),
    )
    titel = models.CharField(
        _("titel"),
        max_length=100,
        help_text=_("Titel van de taak (max. 1 zin)"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        default=StatusTaak.OPEN,
        choices=StatusTaak.choices,
        help_text=_("Status van de taak"),
    )
    startdatum = models.DateTimeField(
        _("start datum"),
        default=timezone.now,
        help_text=_("Startdatum van de taak."),
    )
    handelings_perspectief = models.CharField(
        _("handelings perspectief"),
        max_length=100,
        help_text=_("Handelings perspectief"),
    )
    einddatum_handelings_termijn = models.DateTimeField(
        _("einddatum handelings termijn"),
        blank=True,
        null=True,
        help_text=_("Einddatum handelings termijn"),
    )
    datum_herinnering = models.DateTimeField(
        _("datum herinnering"),
        blank=True,
        null=True,
        help_text=_("Datum Herinnering"),
    )
    toelichting = models.TextField(
        _("toelichting"),
        blank=True,
        help_text=_("Uitleg van de taak"),
    )
    taak_soort = models.CharField(
        _("taak soort"),
        max_length=20,
        choices=SoortTaak.choices,
        help_text=_("Het soort taak"),
    )
    details = JSONField(
        _("details"),
        default=dict,
        help_text=_("Details van de taak met validaties op basis van het soort taak"),
        encoder=DjangoJSONEncoder,
    )

    # TODO relations with URNField:
    # "isToegewezenAan": { "urn": "urn(persoon)", "omschrijving": "string(200)"}
    # "wordtBehandeldDoor": {"urn": "urn(medewerker)", "omschrijving": "string(200)"}
    # "hoortBij": {"urn": "urn(zaak)", "omschrijving": "string(200)"}
    # "heeftBetrekkingOp": {"urn": "urn(product)", "omschrijving": "string(200)"}
    class Meta:
        verbose_name = _("Externe taak")
        verbose_name_plural = _("Externe taken")

    def __str__(self):
        return f"{self.titel} ({self.status})"

    def clean(self):
        super().clean()
        try:
            validate_jsonschema(self.details, self.taak_soort)
        except ValidationError as error:
            raise ValidationError({"details": str(error)})

        try:
            validate_date(self.startdatum, self.einddatum_handelings_termijn)
        except ValidationError as error:
            raise ValidationError({"einddatum_handelings_termijn": error})
