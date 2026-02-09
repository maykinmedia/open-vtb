from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from vng_api_common.pagination import DynamicPageSizePagination

from ..models import Bericht
from .serializers import BerichtSerializer


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle berichten aan."),
        description=_("Vraag alle berichten aan."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifiek bericht opvragen."),
        description=_("Een specifiek bericht opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een bericht aan."),
        description=_("Maak een bericht aan."),
    ),
)
class BerichtViewset(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Bericht.objects.prefetch_related("bijlagen")
    serializer_class = BerichtSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
