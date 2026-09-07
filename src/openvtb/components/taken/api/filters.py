from django.utils.translation import gettext_lazy as _

from django_filters import filters
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_help_text

from openvtb.utils.filters import URNFilter

from ..models import ExterneTaak


class ExterneTaakFilter(FilterSet):
    is_gerelateerd_aan = filters.CharFilter(
        method="filter_is_gerelateerd_aan",
        help_text=_(
            "Filter op URN aanwezig in de lijst isGerelateerdAan. Exacte match op de URN."
        ),
    )
    is_toegewezen_aan = URNFilter(
        field_name="is_toegewezen_aan",
        help_text=get_help_text("taken.ExterneTaak", "is_toegewezen_aan"),
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

    def filter_is_gerelateerd_aan(self, queryset, name, value):
        return queryset.filter(is_gerelateerd_aan__contains=[{"urn": value}])
