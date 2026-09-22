import re

import django_filters
from django_filters.constants import EMPTY_VALUES


class URNFilter(django_filters.CharFilter):
    """
    Filters by an exact segment of a URN field.

    Unlike a generic substring match (icontains), the value must match
    a whole segment delimited by ``:``.
    """

    @staticmethod
    def get_pattern(value):
        return r"(^|:)" + re.escape(value) + r"(:|$)"

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        pattern = self.get_pattern(value)
        return qs.filter(**{f"{self.field_name}__regex": pattern})


class ListURNFilter(django_filters.CharFilter):
    """
    Filters by an exact URN segment within a JSONField containing a
    list of URNs. Supports two shapes:

    - a list of plain URN strings
    - a list of URN objects
    """

    def __init__(self, *args, json_key="urn", **kwargs):
        self.json_key = json_key
        super().__init__(*args, **kwargs)

    def _get_urn(self, item):
        if isinstance(item, dict):
            return item.get(self.json_key, "")
        return item or ""

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        pattern = re.compile(URNFilter.get_pattern(value))

        matching_pks = [
            pk
            for pk, items in qs.values_list("pk", self.field_name)
            if any(pattern.search(self._get_urn(item)) for item in items or [])
        ]
        return qs.filter(pk__in=matching_pks)
