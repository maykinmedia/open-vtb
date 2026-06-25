from vng_api_common.filtersets import FilterSet

from ..models import ExterneTaak


class ExterneTaakFilter(FilterSet):
    class Meta:
        model = ExterneTaak
        fields = {
            "uuid": ["exact"],
            "titel": ["exact"],
            "status": ["exact"],
            "handelings_perspectief": ["exact"],
            "is_toegewezen_aan": ["exact"],
            "startdatum": ["exact", "gt", "gte", "lt", "lte"],
            "einddatum_handelings_termijn": ["exact", "gt", "gte", "lt", "lte"],
            "datum_herinnering": ["exact", "gt", "gte", "lt", "lte"],
        }
