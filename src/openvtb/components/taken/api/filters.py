from django.utils.translation import gettext_lazy as _

from vng_api_common.filtersets import FilterSet

from openvtb.utils.filters import ListURNFilter, URNFilter

from ..models import ExterneTaak


class ExterneTaakFilter(FilterSet):
    is_gerelateerd_aan = ListURNFilter(
        field_name="is_gerelateerd_aan",
        help_text=_(
            "Filter op URN aanwezig in de lijst isGerelateerdAan. "
            "Exacte match op een volledig URN-segment (gescheiden door `:`)."
        ),
    )
    is_toegewezen_aan = URNFilter(
        field_name="is_toegewezen_aan",
        help_text=_(
            "Filtert op een exacte match van een volledig segment van de URN "
            "(gescheiden door `:`) in het veld `is_toegewezen_aan`."
        ),
    )

    class Meta:
        model = ExterneTaak
        fields = {
            "uuid": ["exact"],
            "titel": ["exact"],
            "status": ["exact"],
            "taak_soort": ["exact"],
            "verwerker_taak_id": ["exact"],
            "handelings_perspectief": ["exact"],
            "startdatum": ["exact", "gt", "gte", "lt", "lte"],
            "einddatum_handelings_termijn": ["exact", "gt", "gte", "lt", "lte"],
            "datum_herinnering": ["exact", "gt", "gte", "lt", "lte"],
        }
