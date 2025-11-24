from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from rest_framework_nested.viewsets import NestedViewSetMixin as _NestedViewSetMixin


class NestedViewSetMixin(_NestedViewSetMixin):
    def get_queryset(self):
        """
        Catch validation errors if parent_lookup_kwargs have incorrect format and return 404
        """
        try:
            queryset = super().get_queryset()
        except ValidationError:
            raise Http404

        return queryset


verzoektype_uuid_param = OpenApiParameter(
    name="verzoektype_uuid",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    required=True,
    description=_("UUID van het VerzoekType"),
)
