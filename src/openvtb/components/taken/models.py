import uuid as _uuid

from django.contrib.postgres.indexes import GinIndex
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

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
        max_length=255,
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
        blank=True,  # TODO check if is possible to create without
        choices=SoortTaak.choices,
        help_text=_("Het soort taak"),
    )
    data = models.JSONField(
        _("data"),
        default=dict,
        help_text=_("Data van de taak met validaties op basis van het soort taak"),
        encoder=DjangoJSONEncoder,
    )

    # TODO relations with URNField:
    # "isToegewezenAan": { "urn": "urn(persoon)", "omschrijving": "string(200)"}
    # "wordtBehandeldDoor": {"urn": "urn(medewerker)", "omschrijving": "string(200)"}
    # "hoortBij": {"urn": "urn(zaak)", "omschrijving": "string(200)"}
    # "heeftBetrekkingOp": {"urn": "urn(product)", "omschrijving": "string(200)"}

    class Meta:
        indexes = [GinIndex(fields=["data"], name="idx_externe_taak_data_gin")]

    def __str__(self):
        return f"{self.title} ({self.status})"
