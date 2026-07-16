from vng_api_common.filtersets import FilterSet

from ..models import VerzoekType


class VerzoekTypeFilter(FilterSet):
    class Meta:
        model = VerzoekType
        fields = {
            "uuid": ["exact"],
            "naam": ["exact"],
            "omschrijving": ["icontains"],
        }
