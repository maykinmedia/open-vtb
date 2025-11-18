import uuid
from datetime import date

from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_jsonform.models.fields import JSONField

from openvtb.utils.validators import validate_jsonschema

from .constants import VerzoektypeOpvolging, VerzoekTypeVersionStatus
from .utils import check_json_schema


class VerzoekType(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het VerzoekType"),
    )

    # TODO urn = urnField()

    naam = models.CharField(
        _("naam"),
        max_length=100,
        help_text=_("Naam voor het VerzoekType"),
    )
    toelichting = models.TextField(
        _("toelichting"),
        blank=True,
        help_text=_("Uitleg over het VerzoekType"),
    )
    opvolging = models.CharField(
        _("opvolging"),
        max_length=20,
        default=VerzoektypeOpvolging.NIET_TOT_ZAAK,  # TODO chek for default
        choices=VerzoektypeOpvolging.choices,
        help_text=_("Opvolging over het VerzoekType"),
    )
    created_at = models.DateField(
        _("created at"),
        auto_now_add=True,
        help_text=_("Datum waarop het VerzoekType is aangemaakt"),
    )
    modified_at = models.DateField(
        _("modified at"),
        auto_now=True,
        help_text=_("Laatste datum waarop het VerzoekType is gewijzigd"),
    )
    # TODO bijlageTypen -> DOCUMENTTYPE URN?

    class Meta:
        verbose_name = _("VerzoekType")
        verbose_name_plural = _("VerzoekTypes")

    def __str__(self):
        if self.last_version:
            return f"{self.naam} {self.last_version}"
        return f"{self.naam}"

    @property
    def last_version(self):
        if self.versions:
            return self.versions.order_by("-version").first()
        return None

    @property
    def status(self):
        if self.last_version:
            return self.last_version.status
        return ""

    @property
    def ordered_versions(self):
        return self.versions.order_by("-version")


class VerzoekTypeVersion(models.Model):
    verzoek_type = models.ForeignKey(
        VerzoekType,
        on_delete=models.CASCADE,
        related_name="versions",
        help_text=_("Het VerzoekType waartoe deze versie behoort."),
    )
    version = models.PositiveSmallIntegerField(
        _("version"),
        help_text=_("Integer-versie van het VerzoekType."),
    )
    created_at = models.DateField(
        _("created at"),
        auto_now_add=True,
        help_text=_("Datum waarop de versie is gemaakt"),
    )
    modified_at = models.DateField(
        _("modified at"),
        auto_now=True,
        help_text=_("Laatste datum waarop de versie is gewijzigd"),
    )
    published_at = models.DateField(
        _("published_at"),
        null=True,
        blank=True,
        help_text=_("Datum waarop de versie is gepubliceerd"),
    )
    aanvraag_gegevens_schema = JSONField(
        _("aanvraag gegevens schema"),
        default=dict,
        help_text=_("JSON schema voor validatie van VerzoekType"),
        encoder=DjangoJSONEncoder,
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=VerzoekTypeVersionStatus.choices,
        default=VerzoekTypeVersionStatus.DRAFT,
        help_text=_("Status van het VerzoekTypeVersion"),
    )

    class Meta:
        unique_together = ("verzoek_type", "version")
        ordering = ["-version", "-created_at"]

    def __str__(self):
        return f"Version {self.version} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.version:
            self.version = self.generate_version_number()

        # save published_at
        previous_status = (
            VerzoekTypeVersion.objects.get(id=self.id).status if self.id else None
        )
        if (
            self.status == VerzoekTypeVersionStatus.PUBLISHED
            and previous_status != self.status
        ):
            self.published_at = date.today()

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        try:
            check_json_schema(self.aanvraag_gegevens_schema)
        except ValidationError as error:
            raise ValidationError({"aanvraag_gegevens_schema": str(error)})

    def generate_version_number(self):
        last_version = VerzoekTypeVersion.objects.filter(
            verzoek_type=self.verzoek_type
        ).aggregate(max_version=models.Max("version"))["max_version"]
        return (last_version or 0) + 1


class VerzoekBron(models.Model):
    verzoek = models.OneToOneField(
        "Verzoek",
        on_delete=models.CASCADE,
        related_name="bron",
    )
    naam = models.CharField(
        _("bron naam"),
        max_length=100,
        help_text=_("Naam van de bron."),
    )
    kenmerk = models.CharField(
        _("bron kenmerk"),
        max_length=255,
        help_text=_("Kenmerk van de bron."),
    )

    class Meta:
        verbose_name = _("Verzoek Bron")
        verbose_name_plural = _("Verzoeken Bron")

    def __str__(self):
        return self.naam


class VerzoekBetaling(models.Model):
    verzoek = models.OneToOneField(
        "Verzoek",
        on_delete=models.CASCADE,
        related_name="betaling",
    )
    kenmerken = ArrayField(
        models.CharField(_("kenmerken"), max_length=100),
        blank=True,
        default=list,
        help_text=_("Eventuele kenmerken van de betaling."),
    )
    bedrag = models.DecimalField(
        _("bedrag"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Het bedrag van de betaling."),
    )
    voltooid = models.BooleanField(
        _("voltooid"),
        default=False,
        help_text=_("Geeft aan of de betaling voltooid is."),
    )
    transactie_datum = models.DateTimeField(
        _("transactie datum"),
        blank=True,
        null=True,
        help_text=_("Datum en tijd van de transactie."),
    )
    transactie_referentie = models.CharField(
        _("transactie referentie"),
        max_length=100,
        help_text=_("Referentie van de transactie."),
    )

    class Meta:
        verbose_name = _("Verzoek Betaling")
        verbose_name_plural = _("Verzoeken Betaling")

    def __str__(self):
        return f"{self.verzoek} ({str(self.bedrag)})"


class Verzoek(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het Verzoek."),
    )

    # TODO urn = urnField()

    verzoek_type = models.ForeignKey(
        VerzoekType,
        db_index=True,
        on_delete=models.PROTECT,
        help_text=_("Type van het Verzoek."),
    )
    geometrie = GeometryField(
        _("geometrie"),
        blank=True,
        null=True,
        help_text=_(
            "Point, LineString of Polygon object dat de locatie van het verzoek representeert."
        ),
    )
    aanvraag_gegevens = JSONField(
        _("aanvraag gegevens"),
        default=dict,
        help_text=_("JSON data voor validatie van het VerzoekType."),
        encoder=DjangoJSONEncoder,
    )
    bijlagen = ArrayField(
        models.CharField(
            _("documents"), max_length=100
        ),  # TODO documents URNField ENKELVOUDIGINFORMATIEOBJECT
        blank=True,
        default=list,
        help_text=_("Eventuele bijlagen van het Verzoek (URNs van documenten)."),
    )

    # TODO relations
    # auth_context ->  URNField
    # partij ->  URNField
    # betrokkene ->  URNField
    # zaak ->  URNField

    class Meta:
        verbose_name = _("Verzoek")
        verbose_name_plural = _("Verzoeken")

    def __str__(self):
        return f"{self.uuid}"

    def clean(self):
        super().clean()
        if not self.verzoek_type.last_version:
            raise ValidationError(
                {
                    "verzoek_type": _(
                        "Onbekend VerzoekenType schema: geen schema beschikbaar."
                    )
                },
                code="unknown_choice",
            )
        try:
            validate_jsonschema(
                self.aanvraag_gegevens,
                self.verzoek_type.last_version.aanvraag_gegevens_schema,
            )
        except ValidationError as error:
            raise ValidationError({"aanvraag_gegevens": str(error)})
