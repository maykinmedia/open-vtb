import uuid
from datetime import date

from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from openvtb.components.utils.schemas import IS_INGEDIEND_DOOR_SCHEMA
from openvtb.utils.constants import Valuta
from openvtb.utils.fields import URNField
from openvtb.utils.json_utils import check_json_schema
from openvtb.utils.validators import validate_jsonschema

from .constants import VerzoekTypeVersionStatus


class VerzoekType(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het VerzoekType"),
    )
    naam = models.CharField(
        _("naam"),
        max_length=100,
        help_text=_("Naam voor het VerzoekType"),
    )
    toelichting = models.TextField(
        _("toelichting"),
        max_length=4000,
        blank=True,
        help_text=_("Uitleg over het VerzoekType"),
    )
    aangemaakt_op = models.DateField(
        _("aangemaakt op"),
        auto_now_add=True,
        help_text=_("Datum waarop het VerzoekType is aangemaakt"),
    )
    gewijzigd_op = models.DateField(
        _("gewijzigd op"),
        auto_now=True,
        help_text=_("Laatste datum waarop het VerzoekType is gewijzigd"),
    )

    class Meta:
        verbose_name = _("VerzoekType")
        verbose_name_plural = _("VerzoekTypes")

    def __str__(self):
        return self.naam

    @property
    def last_version(self):
        if self.versions:
            return self.versions.order_by("-version").first()
        return None

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
    aangemaakt_op = models.DateField(
        _("aangemaakt op"),
        auto_now_add=True,
        help_text=_("Datum waarop de versie is gemaakt"),
    )
    gewijzigd_op = models.DateField(
        _("gewijzigd op"),
        auto_now=True,
        help_text=_("Laatste datum waarop de versie is gewijzigd"),
    )
    begin_geldigheid = models.DateField(
        _("begin geldigheid"),
        null=True,
        blank=True,
        help_text=_("Datum waarop de versie is gepubliceerd"),
    )
    einde_geldigheid = models.DateField(
        _("einde geldigheid"),
        default=None,
        null=True,
        help_text=_(
            "Einde van de geldigheidsduur van de versie, automatisch ingesteld wanneer een nieuwere versie wordt gepubliceerd. "
            "Als de waarde wordt ingesteld voordat de versie wordt gepubliceerd, wordt deze overschreven met de publicatiedatum."
        ),
    )

    aanvraag_gegevens_schema = models.JSONField(
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
        ordering = ["-version", "-aangemaakt_op"]

    def __str__(self):
        return f"Version {self.version} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.version:
            self.version = self.generate_version_number()

        # save published_at and set previouos version as expired
        previous_status = (
            VerzoekTypeVersion.objects.get(id=self.id).status if self.id else None
        )
        if (
            self.status == VerzoekTypeVersionStatus.PUBLISHED
            and previous_status != self.status
        ):
            self.begin_geldigheid = date.today()
            if (
                previous_version := VerzoekTypeVersion.objects.filter(
                    verzoek_type=self.verzoek_type
                )
                .exclude(id=self.id)
                .first()
            ):
                previous_version.einde_geldigheid = date.today()
                previous_version.save()

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return bool(self.einde_geldigheid and self.einde_geldigheid <= date.today())

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
        blank=True,
        help_text=_("Naam van de bron."),
    )
    kenmerk = models.CharField(
        _("bron kenmerk"),
        max_length=255,
        blank=True,
        help_text=_("Kenmerk van de bron."),
    )

    class Meta:
        verbose_name = _("Verzoek Bron")
        verbose_name_plural = _("Verzoeken Bron")

    def __str__(self):
        return self.naam


# TODO check optional fields
class VerzoekBetaling(models.Model):
    verzoek = models.OneToOneField(
        "Verzoek",
        on_delete=models.CASCADE,
        related_name="betaling",
    )
    kenmerken = ArrayField(
        models.CharField(_("kenmerken"), max_length=100),
        blank=True,
        null=True,
        default=list,
        help_text=_("Eventuele kenmerken van de betaling."),
    )
    bedrag = models.DecimalField(
        _("bedrag"),
        max_digits=10,
        null=True,
        decimal_places=2,
        help_text=_("Het bedrag van de betaling."),
    )
    valuta = models.CharField(
        _("valuta"),
        max_length=20,
        default=Valuta.EUR,
        choices=Valuta.choices,
        help_text=_("Valuta van de betaling"),
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
        blank=True,
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
    verzoek_type = models.ForeignKey(
        VerzoekType,
        db_index=True,
        on_delete=models.PROTECT,
        help_text=_("Type van het Verzoek."),
    )
    version = models.PositiveSmallIntegerField(
        _("version"),
        help_text=_(
            "Versie van VerzoekType om het gegevensschema van het verzoek te valideren"
        ),
    )
    geometrie = GeometryField(
        _("geometrie"),
        blank=True,
        null=True,
        help_text=_(
            "Point, LineString of Polygon object dat de locatie van het verzoek representeert."
        ),
    )
    aanvraag_gegevens = models.JSONField(
        _("aanvraag gegevens"),
        default=dict,
        help_text=_("JSON data voor validatie van het VerzoekType."),
        encoder=DjangoJSONEncoder,
    )
    is_ingediend_door = models.JSONField(
        _("Is ingediend door"),
        default=dict,
        blank=True,
        help_text=_(
            "JSON-object dat aangeeft door wie het verzoek is ingediend. "
            "Kan één van de volgende vormen hebben:\n"
            "- authentiekeVerwijzing: object met een 'urn' string (bijv. 'urn:...')\n"
            "- nietAuthentiekePersoonsgegevens: object met persoonsgegevens zoals voornaam, achternaam, geboortedatum, emailadres, telefoonnummer, postadres en verblijfsadres\n"
            "- nietAuthentiekeOrganisatiegegevens: object met organisatiegegevens zoals statutaireNaam, bezoekadres, postadres, emailadres en telefoonnummer\n"
            "Dit JSON-object wordt gebruikt voor validatie van het VerzoekType."
        ),
        encoder=DjangoJSONEncoder,
    )
    is_gerelateerd_aan = URNField(
        _("is gerelateerd aan"),
        help_text=_(
            "URN naar de ZAAK of het PRODUCT. Bijvoorbeeld: `urn:nld:gemeenteutrecht:zaak:zaaknummer:000350165`"
        ),
        blank=True,
    )
    kanaal = models.CharField(
        _("kanaal"),
        blank=True,
        max_length=200,
        help_text=_("Geeft aan via welk kanaal dit verzoek is binnengekomen."),
    )
    # authenticatie_context relation
    authenticatie_context = URNField(
        _("authenticatie context"),
        help_text=_("authentication context urn"),  # TODO check help_text
        blank=True,
    )
    informatie_object = URNField(
        _("informatie object"),
        help_text=_(
            "URN naar het ENKELVOUDIGINFORMATIEOBJECT zijnde het verzoek als document zoals gezien door de aanvrager."
        ),
        blank=True,
    )

    class Meta:
        verbose_name = _("Verzoek")
        verbose_name_plural = _("Verzoeken")

    def __str__(self):
        return f"{self.uuid}"

    def clean_is_ingediend_door(self):
        if not self.is_ingediend_door:
            return

        if len(self.is_ingediend_door.keys()) > 1:
            raise ValidationError(
                {
                    "is_ingediend_door": _(
                        "It must have only one of the three permitted keys: "
                        "one of `authentiekeVerwijzing`, `nietAuthentiekePersoonsgegevens` or `nietAuthentiekeOrganisatiegegevens`."
                    )
                },
                code="invalid",
            )
        try:
            validate_jsonschema(
                instance=self.is_ingediend_door,
                label="is_ingediend_door",
                schema=IS_INGEDIEND_DOOR_SCHEMA,
            )
        except ValidationError as error:
            raise ValidationError({"is_ingediend_door": str(error)})

    def clean_verzoek_type(self):
        if not self.verzoek_type_id:
            return
        if not self.verzoek_type.versions.filter(version=self.version).exists():
            raise ValidationError(
                {
                    "version": _(
                        "Onbekend VerzoekType schema versie: geen schema beschikbaar."
                    )
                },
                code="unknown-schema",
            )

        try:
            validate_jsonschema(
                instance=self.aanvraag_gegevens,
                label="aanvraag_gegevens",
                schema=self.verzoek_type.versions.get(
                    version=self.version
                ).aanvraag_gegevens_schema,
            )
        except ValidationError as error:
            raise ValidationError({"aanvraag_gegevens": str(error)})

    def clean(self):
        super().clean()
        self.clean_verzoek_type()
        self.clean_is_ingediend_door()


class Bijlage(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het Bijlage."),
    )
    verzoek = models.ForeignKey(
        Verzoek,
        on_delete=models.CASCADE,
        related_name="bijlagen",
        help_text=_("Bijlagen gekoppeld aan het Verzoek."),
    )
    informatie_object = URNField(
        _("informatie object"),
        help_text=_(
            "URN naar het ENKELVOUDIGINFORMATIEOBJECT. "
            "Bijvoorbeeld: `urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e`"
        ),
        blank=True,
    )
    toelichting = models.TextField(
        _("toelichting"),
        max_length=4000,
        blank=True,
        help_text=_(
            "Toelichting van de bijlage, zoals die door eindgebruikers gezien kan worden in bijvoorbeeld een portaal. "
            "Typisch is dit dezelfde omschrijving als die van het INFORMATIEOBJECT."
        ),
    )

    class Meta:
        verbose_name = _("Bijlage")
        verbose_name_plural = _("Bijlagen")
        unique_together = ("verzoek", "informatie_object")

    def __str__(self):
        return self.informatie_object


class BijlageType(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het BijlageType."),
    )
    verzoek_type_version = models.ForeignKey(
        VerzoekTypeVersion,
        on_delete=models.CASCADE,
        related_name="bijlage_typen",
        help_text=_("Bijlagetypen gekoppeld aan het VerzoekTypeVersion."),
    )
    informatie_objecttype = URNField(
        _("informatie objecttype"),
        help_text=_(
            "URN van het INFORMATIEOBJECTTYPE. "
            "Bijvoorbeeld: `urn:nld:gemeenteutrecht:informatieobjecttype:uuid:717815f6-1939-4fd2-93f0-83d25bad154e`"
        ),
        blank=True,
    )
    omschrijving = models.TextField(
        _("omschrijving"),
        blank=True,
        help_text=_(
            "Omschrijving van het soort bijlage, zoals dat door eind gebruikers gezien kan worden in bijvoorbeeld een portaal. "
            "Typisch is dit dezelfde omschrijving als die van het INFORMATIEOBJECTTYPE."
        ),
    )

    class Meta:
        verbose_name = _("BijlageType")
        verbose_name_plural = _("BijlageTypen")

        unique_together = ("verzoek_type_version", "informatie_objecttype")

    def __str__(self):
        return self.informatie_objecttype
