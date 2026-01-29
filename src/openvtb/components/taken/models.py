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

from .constants import ActionTaak, SoortTaak, StatusTaak
from .schemas import FORMULIER_DEFINITIE_SCHEMA
from .utils import get_json_schema


class ExterneTaak(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text=(
            "Een UUID waarmee een ZAC een link kan leggen tussen "
            "de taak en zijn eigen administratie."
        ),
    )
    titel = models.CharField(
        _("titel"),
        max_length=100,
        help_text=_(
            "Titel van de uit te voeren taak, zoals dat door eind "
            "gebruikers gezien kan worden in bijvoorbeeld een portaal."
        ),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        default=StatusTaak.OPEN,
        choices=StatusTaak.choices,
        help_text=_("Status van de taak."),
    )
    startdatum = models.DateTimeField(
        _("start datum"),
        default=timezone.now,
        help_text=_("Startdatum van de taak."),
    )
    handelings_perspectief = models.CharField(
        _("handelings perspectief"),
        max_length=100,
        blank=True,
        choices=ActionTaak.choices,
        help_text=_(
            "De door de toegewezen persoon of bedrijf uit te voeren handeling."
        ),
    )
    einddatum_handelings_termijn = models.DateTimeField(
        _("einddatum handelings termijn"),
        blank=True,
        null=True,
        help_text=_("Einddatum handelings termijn."),
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
        help_text=_(
            "Toelichting van de uit te voeren taak, zoals dat door eind gebruikers "
            "gezien kan worden in bijvoorbeeld een portaal."
        ),
    )
    taak_soort = models.CharField(
        _("taak soort"),
        max_length=20,
        choices=SoortTaak.choices,
        help_text=_("Het soort taak."),
    )
    details = JSONField(
        _("details"),
        default=dict,
        help_text=_("De attributen die horen bij de `taakSoort`."),
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
            "URN naar de ZAAK. "
            "Bijvoorbeeld: urn:nld:gemeenteutrecht:zaak:zaaknummer:000350165"
        ),
        blank=True,
    )
    # product relation
    heeft_betrekking_op = URNField(
        _("heeft betrekking op product"),
        help_text=_(
            "URN naar het PRODUCT. "
            "Bijvoorbeeld: urn:nld:gemeenteutrecht:product:uuid:717815f6-1939-4fd2-93f0-83d25bad154e"
        ),
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
