import uuid
from datetime import date

from django.contrib.gis.db.models import GeometryField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from openvtb.components.schemas import IS_GERELATEERD_AAN_SCHEMA
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
    omschrijving = models.TextField(
        _("omschrijving"),
        max_length=4000,
        blank=True,
        help_text=_(
            "Interne omschrijving van het type verzoek. Bijvoorbeeld om de relatie naar het zaaktype te schetsen."
        ),
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
    def last_versie(self):
        return self.versies.order_by("-versie").first()


class VerzoekTypeVersion(models.Model):
    verzoek_type = models.ForeignKey(
        VerzoekType,
        on_delete=models.CASCADE,
        related_name="versies",
        help_text=_("Het VerzoekType waartoe deze versie behoort."),
    )
    versie = models.PositiveSmallIntegerField(
        _("versie"),
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
        unique_together = ("verzoek_type", "versie")
        ordering = ["-versie", "-aangemaakt_op"]

    def __str__(self):
        return f"{self.verzoek_type} v{self.versie}"

    def save(self, *args, **kwargs):
        if not self.versie:
            self.versie = self.generate_versie_number()

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
                previous_versie := VerzoekTypeVersion.objects.filter(
                    verzoek_type=self.verzoek_type
                )
                .exclude(id=self.id)
                .first()
            ):
                previous_versie.einde_geldigheid = date.today()
                previous_versie.save()

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return bool(self.einde_geldigheid and self.einde_geldigheid <= date.today())

    def bijlage_typen_list(self):
        bijlage_typen = self.bijlage_typen.all()
        if not bijlage_typen:
            return _("Geen bijlagentypen")

        display_list = []
        for bijlage_type in bijlage_typen:
            url = reverse("admin:verzoeken_bijlagetype_change", args=[bijlage_type.id])
            display_list.append(
                '<a href="{url}">{text}</a>'.format(
                    url=url, text=bijlage_type.informatie_objecttype
                )
            )

        return format_html("<br><br>".join(display_list))

    def clean(self):
        super().clean()
        try:
            check_json_schema(self.aanvraag_gegevens_schema)
        except ValidationError as error:
            raise ValidationError({"aanvraag_gegevens_schema": str(error)})

    def generate_versie_number(self):
        last_versie = VerzoekTypeVersion.objects.filter(
            verzoek_type=self.verzoek_type
        ).aggregate(max_versie=models.Max("versie"))["max_versie"]
        return (last_versie or 0) + 1


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
        help_text=_("De naam van de bron applicatie die dit verzoek heeft aangemaakt."),
    )
    kenmerk = models.CharField(
        _("bron kenmerk"),
        max_length=255,
        blank=True,
        help_text=_(
            "Een kenmerk of identificatie van de specifieke instantie die in de bron applicatie "
            "heeft geleid tot dit verzoek. Bijvoorbeeld een inzendingsnummer."
        ),
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
    provider_kenmerk = models.CharField(
        _("provider kenmerk"),
        max_length=100,
        blank=True,
        help_text=_(
            "Een kenmerk (bijv. het PSP ID van Worldline) dat aangeeft welke provider de betaling moet afhandelen."
        ),
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
        help_text=_(
            "Een nummer of code die volgt vanuit de"
            "betaalprovider na het voltooien van de transactie. Hiermee wordt de transactie "
            "administratief gekoppeld aan het verzoek."
        ),
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
    versie = models.PositiveSmallIntegerField(
        _("versie"),
        help_text=_(
            "Indien geen waarde is opgegeven wordt de laatste versie van het VERZOEKTYPE gebruikt."
        ),
        blank=True,
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
    initiator = URNField(
        _("initiator"),
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
        help_text=_("Lijst van URN's naar ZAAK of PRODUCT."),
        encoder=DjangoJSONEncoder,
    )
    kanaal = models.CharField(
        _("kanaal"),
        blank=True,
        max_length=200,
        help_text=_("Geeft aan via welk kanaal dit verzoek is binnengekomen."),
    )
    verzoek_informatie_object = URNField(
        _("verzoek informatie object"),
        help_text=_(
            "URN naar het ENKELVOUDIGINFORMATIEOBJECT zijnde het verzoek als document zoals gezien door de aanvrager."
            "Bijvoorbeeld: `urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e`"
        ),
        blank=True,
    )
    verzoek_taal = models.CharField(
        _("verzoek taal"),
        help_text=_(
            "De taal, volgens het IANA Language Subtag Registry, waarin het verzoek is gedaan. "
            "In de meest praktische vorm is dit de taal van de vragen maar het is mogelijk dat de "
            "antwoorden in een andere taal zijn gedaan. Bijvoorbeeld door iemand die wel Nederlands "
            "kan lezen maar niet kan schrijven."
        ),
        max_length=2,
        validators=[MinLengthValidator(limit_value=2)],
        default="nl",
        blank=True,
    )

    class Meta:
        verbose_name = _("Verzoek")
        verbose_name_plural = _("Verzoeken")

    def __str__(self):
        return f"{self.uuid}"

    def save(self, *args, **kwargs):
        if not self.versie and self.verzoek_type.last_versie:
            self.versie = self.verzoek_type.last_versie.versie

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

    def clean_verzoek_type(self):
        if not self.verzoek_type_id:
            return

        if not self.verzoek_type.versies.filter(versie=self.versie).exists():
            raise ValidationError(
                {
                    "versie": _(
                        "Onbekend VerzoekType schema versie: geen schema beschikbaar."
                    )
                },
                code="unknown-schema",
            )

        try:
            validate_jsonschema(
                instance=self.aanvraag_gegevens,
                label="aanvraag_gegevens",
                schema=self.verzoek_type.versies.get(
                    versie=self.versie
                ).aanvraag_gegevens_schema,
            )
        except ValidationError as error:
            raise ValidationError({"aanvraag_gegevens": str(error)})

    def clean(self):
        super().clean()
        self.clean_verzoek_type()
        self.clean_is_gerelateerd_aan()


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
    verzoek_type_versie = models.ForeignKey(
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

        unique_together = ("verzoek_type_versie", "informatie_objecttype")

    def __str__(self):
        return self.informatie_objecttype
