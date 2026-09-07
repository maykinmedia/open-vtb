import re

import django_filters
from django_filters.constants import EMPTY_VALUES


class URNFilter(django_filters.CharFilter):
    """
    Filters by an exact segment of a URN field.

    Unlike a generic substring match (icontains), the value must match
    a whole segment delimited by ``:``
    Example usage
    -------------
        class ZaakFilterSet(django_filters.FilterSet):
            identificatie = URNFilter(field_name="identificatie")

    """

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        pattern = r"(^|:)" + re.escape(value) + r"(:|$)"
        return qs.filter(**{f"{self.field_name}__regex": pattern})
