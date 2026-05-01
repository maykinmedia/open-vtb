import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from openvtb.utils.fields import URNField


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
        help_text=_("Zenderreferentie / interne referentie."),
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
    bericht_type = models.CharField(
        _("bericht type"),
        max_length=8,
        blank=True,
        help_text=_(
            "Een code voor het technisch identificeren van een bericht soort & origine. "
            "Wordt ook gebruikt in de Mijn Overheid berichtenbox."
        ),
    )
    handelings_perspectief = models.CharField(
        _("handelings perspectief"),
        max_length=50,
        blank=True,
        help_text=_(
            "De door de toegewezen persoon of bedrijf uit te voeren handeling. "
            "Bijvoorbeeld: `lezen`, `naleveren`, `invullen`."
        ),
    )
    einddatum_handelings_termijn = models.DateTimeField(
        _("einddatum handelings termijn"),
        null=True,
        help_text=_("Datum/tijd waarop handeling afgerond moet zijn."),
    )

    class Meta:
        verbose_name = _("Bericht")
        verbose_name_plural = _("Berichten")

    def __str__(self):
        return self.onderwerp


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
            "Een korte omschrijving of de titel van de bijlage. Deze wordt typisch getoond in een portaal."
        ),
    )
    is_bericht_type_bijlage = models.BooleanField(
        _("is bericht type bijlage"),
        default=False,
        help_text=_(
            "Geeft aan of dit document een standaardbijlage is die vooraf geüpload is in het Berichtenbox Leveranciersportaal. "
            "Standaard `false`. Indien `true` moet deze bijlage door het outputmanagementcomponent "
            "genegeerd worden - als de Berichtenbox het doelkanaal is."
        ),
    )

    class Meta:
        verbose_name = _("Bericht bijlage")
        verbose_name_plural = _("Berichten bijlagen")
        unique_together = ("bericht", "informatie_object")

    def __str__(self):
        return self.informatie_object
