import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from polymorphic.models import PolymorphicModel
from relativedeltafield import RelativeDeltaField

from .constants import StatusTaak


class ExterneTaak(PolymorphicModel):
    verwerker_taak_id = models.UUIDField(
        _("verwerker taak id"),
        default=uuid.uuid4,
        help_text=_(
            "Een UUID waarmee een ZAC een link kan leggen tussen de taak en zijn eigen administratie."
        ),
    )
    titel = models.CharField(
        _("titel"),
        max_length=255,
        help_text=_("Titel van de taak (max. 1 zin)"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        default=StatusTaak.OPEN,
        choices=StatusTaak.choices,
    )

    startdatum = models.DateTimeField(
        _("start datum"),
        blank=True,
        null=True,
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
    )

    # TODO:
    # "isToegewezenAan": { "urn": "urn(persoon)", "omschrijving": "string(200)"}
    # "wordtBehandeldDoor": {"urn": "urn(medewerker)", "omschrijving": "string(200)"}
    # "hoortBij": {"urn": "urn(zaak)", "omschrijving": "string(200)"}
    # "heeftBetrekkingOp": {"urn": "urn(product)", "omschrijving": "string(200)"}


class BetaalTaak(ExterneTaak):
    pass


class GegevensUitvraagTaak(ExterneTaak):
    pass


class FormulierTaak(ExterneTaak):
    pass
