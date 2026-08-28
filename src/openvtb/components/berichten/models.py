import uuid

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from openvtb.components.constants import HandelingsPerspectiefEnum
from openvtb.components.schemas import IS_GERELATEERD_AAN_SCHEMA
from openvtb.utils.fields import URNField
from openvtb.utils.validators import validate_jsonschema


class BerichtType(models.Model):
    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het BerichtType."),
    )
    handelings_perspectief = models.CharField(
        _("handelings perspectief"),
        max_length=50,
        blank=True,
        choices=HandelingsPerspectiefEnum.choices,
        help_text=_(
            "De door de toegewezen persoon of bedrijf uit te voeren handeling."
        ),
    )
    mijn_overheid_berichtenbox = models.BooleanField(
        _("Mijn Overheid Berichtenbox"),
        help_text=_(
            "Geeft aan of berichten van dit type geschikt zijn voor publicatie in de "
            "MijnOverheid Berichtenbox. Als dit op ``False`` staat, zijn berichten "
            "van dit type niet bedoeld voor publicatie in de Berichtenbox."
        ),
    )
    mijn_overheid_berichtenbox_type = models.CharField(
        _("Mijn Overheid Berichtenbox Type"),
        max_length=8,
        blank=True,
        help_text=_(
            "Een code voor het technisch identificeren van een bericht soort & origine. "
            "Wordt gebruikt in de Mijn Overheid berichtenbox."
        ),
    )
    verantwoordelijke_organisatie = URNField(
        _("verantwoordelijke organisatie"),
        help_text=_(
            "Geeft aan welk onderdeel van de organisatie de eigenaar is van dit "
            "berichtType. Kan bijv. gebruikt worden voor routering, administratieve "
            "doeleinden en zichtbaarheid in de keten."
        ),
    )

    class Meta:
        verbose_name = _("BerichtType")
        verbose_name_plural = _("BerichtTypen")

    def __str__(self):
        return str(self.uuid)


class Bericht(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het Bericht."),
    )
    onderwerp = models.CharField(
        _("onderwerp"),
        max_length=50,
        help_text=_("Onderwerp van het bericht."),
    )
    bericht_tekst = models.TextField(
        _("bericht tekst"),
        max_length=4000,
        help_text=_(
            "Tekst van het bericht. URLs worden altijd weergegeven als klikbare URLs op alle portalen. "
            "Voor portalen van lokale overheden is de basic syntax van Markdown toegestaan, "
            "voor de Mijn Overheid berichtenbox enkel newlines (\\r\\n)."
        ),
    )
    publicatiedatum = models.DateTimeField(
        _("publicatiedatum"),
        default=timezone.now,
        null=True,
        help_text=_(
            "Datum/tijd waarop bericht zichtbaar moet worden voor de ontvanger. "
            "Dit geldt voor zowel de Mijn Overheid berichtenbox als het portaal van de lokale overheid. "
            "De standaardwaarde is de huidige datum/tijd."
        ),
    )
    is_gepubliceerd = models.BooleanField(
        _("gepubliceerd"),
        default=False,
        help_text=_(
            "Geeft aan of het object gepubliceerd is en zichtbaar voor gebruikers."
        ),
    )
    referentie = models.CharField(
        _("referentie"),
        max_length=25,
        blank=True,
        help_text=_(
            "Uw eigen optionele referentiegegevens, maximaal 25 tekens, "
            "conform de requirements van Logius in haar technische aansluithandleiding."
        ),
    )
    ontvanger = URNField(
        _("ontvanger"),
        help_text=_(
            "URN van een NATUURLIJK PERSOON of NIET-NATUURLIJK PERSOON. "
            "Bijvoorbeeld: `urn:nld:brp:bsn:111222333`, `urn:nld:hr:kvknummer:444555666` "
            "of `urn:nld:hr:kvknummer:444555666:vestigingsnummer:777888999`"
        ),
    )
    geopend_op = models.DateTimeField(
        _("geopend op"),
        null=True,
        help_text=_(
            "Het bericht is door de geadresseerde geopend op dit tijdstip in het "
            "portaal van de lokale overheid. Deze waarde is onafhankelijk Mijn Overheid."
        ),
    )
    bericht_type = models.ForeignKey(
        BerichtType,
        on_delete=models.PROTECT,
        related_name="berichten",
        verbose_name=_("bericht type"),
        help_text=_("Het berichttype waartoe dit bericht behoort."),
    )
    einddatum_handelings_termijn = models.DateTimeField(
        _("einddatum handelings termijn"),
        null=True,
        help_text=_("Datum/tijd waarop handeling afgerond moet zijn."),
    )
    is_gerelateerd_aan = models.JSONField(
        _("is gerelateerd aan"),
        default=list,
        blank=True,
        null=True,
        help_text=_("Lijst met URN’s naar de ZAAK of het PRODUCT."),
        encoder=DjangoJSONEncoder,
    )

    class Meta:
        verbose_name = _("Bericht")
        verbose_name_plural = _("Berichten")

    def __str__(self):
        return self.onderwerp

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

    def clean(self):
        super().clean()
        self.clean_is_gerelateerd_aan()


class BijlageType(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het BijlageType."),
    )
    bericht_type = models.ForeignKey(
        BerichtType,
        on_delete=models.CASCADE,
        related_name="bijlage_typen",
        verbose_name=_("bericht type"),
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

        unique_together = ("bericht_type", "informatie_objecttype")

    def __str__(self):
        return self.informatie_objecttype


class Bijlage(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke identificatiecode (UUID4) voor het Bijlage."),
    )
    bericht = models.ForeignKey(
        Bericht,
        on_delete=models.CASCADE,
        related_name="bijlagen",
        help_text=_("Bijlagen gekoppeld aan het bericht."),
    )
    informatie_object = URNField(
        _("informatie object"),
        help_text=_(
            "URN naar het ENKELVOUDIGINFORMATIEOBJECT. "
            "Bijvoorbeeld: `urn:nld:gemeenteutrecht:informatieobject:uuid:717815f6-1939-4fd2-93f0-83d25bad154e`"
        ),
    )
    omschrijving = models.CharField(
        _("omschrijving"),
        blank=True,
        max_length=40,
        help_text=_(
            "Een door de inwoner of bedrijf goed leesbare omschrijving van de bijlage die "
            "wordt weergegeven als bestandsnaam in een berichtenbox of portaal."
        ),
    )

    class Meta:
        verbose_name = _("Bericht bijlage")
        verbose_name_plural = _("Berichten bijlagen")
        unique_together = ("bericht", "informatie_object")

    def __str__(self):
        return self.informatie_object
