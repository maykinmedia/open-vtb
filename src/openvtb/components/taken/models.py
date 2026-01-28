import uuid as _uuid

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_jsonform.models.fields import JSONField

from openvtb.utils.fields import URNField
from openvtb.utils.json_utils import get_json_schema
from openvtb.utils.validators import validate_date, validate_jsonschema

from .constants import SoortTaak, StatusTaak
from .schemas import FORMULIER_DEFINITIE_SCHEMA, SOORTTAAK_SCHEMA_MAPPING


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
    # partij relation
    is_toegewezen_aan = URNField(
        _("is toegewezen aan partij"),
        help_text=_(
            "De persoon of partij aan wie deze taak is toegewezen. "
            "Kan een van de volgende types zijn: PARTIJ, NATUURLIJK PERSOON of NIET NATUURLIJK PERSOON."
        ),
        blank=True,
    )
    # medewerker relation
    wordt_behandeld_door = URNField(
        _("wordt behandeld door medewerker"),
        help_text=_(
            "De medewerker die verantwoordelijk is voor de uitvoering van deze taak. "
            "Kan een entiteit van het type MEDEWERKER zijn."
        ),
        blank=True,
    )
    # zaak relation
    hoort_bij = URNField(
        _("hoort bij zaak"),
        help_text=_(
            "De zaak waartoe deze taak behoort, waarmee de taak kan worden gekoppeld aan een specifieke zaak."
        ),
        blank=True,
    )
    # product relation
    heeft_betrekking_op = URNField(
        _("heeft betrekking op product"),
        help_text=_("Het product waarop deze taak betrekking heeft"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Externe taak")
        verbose_name_plural = _("Externe taken")

    def __str__(self):
        return f"{self.titel} ({self.status})"

    def clean(self):
        super().clean()
        try:
            validate_jsonschema(
                instance=self.details,
                label="details",
                schema=get_json_schema(self.taak_soort, SOORTTAAK_SCHEMA_MAPPING),
            )
            if self.taak_soort == SoortTaak.FORMULIERTAAK:
                validate_jsonschema(
                    instance=self.details["formulierDefinitie"],
                    label="formulierDefinitie",
                    schema=FORMULIER_DEFINITIE_SCHEMA,
                )
        except ValidationError as error:
            raise ValidationError({"details": str(error)})

        try:
            validate_date(self.startdatum, self.einddatum_handelings_termijn)
        except ValidationError as error:
            raise ValidationError({"einddatum_handelings_termijn": error})
