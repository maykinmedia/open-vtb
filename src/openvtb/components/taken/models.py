import uuid as _uuid
from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from openvtb.components.schemas import IS_GERELATEERD_AAN_SCHEMA
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
            "Een UUID waarmee een ZAC een link kan leggen tussen "
            "de taak en zijn eigen administratie."
        ),
    )
    titel = models.CharField(
        _("titel"),
        max_length=100,
        help_text=_(
            "Titel van de uit te voeren taak, zoals die door eindgebruikers "
            "gezien kan worden in bijvoorbeeld een portaal."
        ),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        default=StatusTaak.OPEN,
        choices=StatusTaak.choices,
        help_text=_("Status van de taak."),
    )
    startdatum = models.DateField(
        _("start datum"),
        default=date.today,
        help_text=_("Startdatum van de taak."),
    )
    handelings_perspectief = models.CharField(
        _("handelings perspectief"),
        max_length=100,
        blank=True,
        help_text=_(
            "De door de toegewezen persoon of bedrijf uit te voeren handeling. "
            "Bijvoorbeeld: `lezen`, `naleveren`, `invullen`."
        ),
    )
    einddatum_handelings_termijn = models.DateField(
        _("einddatum handelings termijn"),
        help_text=_("Einddatum handelings termijn."),
    )
    datum_herinnering = models.DateField(
        _("datum herinnering"),
        blank=True,
        null=True,
        help_text=_(
            "Stuurt een systeem-notificatie op deze datum op het systeem-ingestelde tijdstip. "
            "Indien deze waarde niet expliciet wordt meegegeven, dan wordt deze waarde automatisch "
            "ingesteld op een systeem-ingesteld aantal dagen voor de 'einddatumHandelingsTermijn'."
        ),
    )
    toelichting = models.CharField(
        _("toelichting"),
        max_length=80,
        blank=True,
        help_text=_(
            "Toelichting van de uit te voeren taak, zoals die door eindgebruikers "
            "gezien kan worden in bijvoorbeeld een portaal."
        ),
    )
    taak_soort = models.CharField(
        _("taak soort"),
        max_length=20,
        choices=SoortTaak.choices,
        help_text=_("Het soort taak."),
    )
    details = models.JSONField(
        _("details"),
        default=dict,
        help_text=_("De attributen die horen bij de `taakSoort`."),
        encoder=DjangoJSONEncoder,
    )
    is_toegewezen_aan = URNField(
        _("is toegewezen aan subject"),
        help_text=_(
            "Verwijzing naar een authentieke of niet-authentieke persoon of organisatie. "
            "Dit kan een URN van een NATUURLIJK PERSOON of NIET-NATUURLIJK PERSOON zijn. "
            "Bijvoorbeeld: `urn:nld:brp:bsn:111222333`, `urn:nld:hr:kvknummer:444555666`, "
            "`urn:nld:hr:kvknummer:444555666:vestigingsnummer:777888999` of "
            "`urn:nld:klant:klantnummer:610541501`"
        ),
        blank=True,
    )
    is_gerelateerd_aan = models.JSONField(
        _("is gerelateerd aan"),
        default=list,
        blank=True,
        null=True,
        help_text=_(
            "URN naar de ZAAK of het PRODUCT. "
            "Bijvoorbeeld: `urn:nld:gemeenteutrecht:zaak:zaaknummer:000350165` "
            "of `urn:nld:gemeenteutrecht:product:uuid:717815f6-1939-4fd2-93f0-83d25bad154e`."
        ),
        encoder=DjangoJSONEncoder,
    )

    class Meta:
        verbose_name = _("Externe taak")
        verbose_name_plural = _("Externe taken")

    def __str__(self):
        return f"{self.titel} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.datum_herinnering:
            if (
                self.einddatum_handelings_termijn
                and settings.TAKEN_DEFAULT_REMINDER_IN_DAYS > 0
            ):
                self.datum_herinnering = self.einddatum_handelings_termijn - timedelta(
                    days=settings.TAKEN_DEFAULT_REMINDER_IN_DAYS
                )
        super().save(*args, **kwargs)

    def clean_is_gerelateerd_aan(self):
        if not self.is_gerelateerd_aan:
            return

        try:
            validate_jsonschema(
                instance=self.is_gerelateerd_aan,
                label="is_gerelateerd_aan",
                schema=IS_GERELATEERD_AAN_SCHEMA,
            )
        except ValidationError as error:
            raise ValidationError({"is_gerelateerd_aan": str(error)})

    def clean_details(self):
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

    def clean_dates(self):
        try:
            # startdatum <= einddatum_handelings_termijn
            validate_date(self.startdatum, self.einddatum_handelings_termijn)

            # datum_herinnering <= einddatum_handelings_termijn
            validate_date(self.datum_herinnering, self.einddatum_handelings_termijn)
        except ValidationError as error:
            raise ValidationError({"einddatum_handelings_termijn": error})

    def clean(self):
        super().clean()

        self.clean_details()
        self.clean_dates()
        self.clean_is_gerelateerd_aan()
