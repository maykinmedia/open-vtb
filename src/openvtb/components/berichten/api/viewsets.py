from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from vng_api_common.pagination import DynamicPageSizePagination

from ..models import Bericht, BerichtOntvanger
from .serializers import BerichtOntvangerSerializer, BerichtSerializer


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
    queryset = Bericht.objects.select_related("ontvanger").prefetch_related("bijlagen")
    serializer_class = BerichtSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle berichtenontvangers aan."),
        description=_("Vraag alle berichtenontvangers aan."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifiek berichtontvanger opvragen."),
        description=_("Een specifiek berichtontvanger opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een berichtontvanger aan."),
        description=_("Maak een berichtontvanger aan."),
    ),
    update=extend_schema(
        summary=_("Volledig berichtontvanger wijzigen."),
        description=_("Volledig berichtontvanger wijzigen."),
    ),
    partial_update=extend_schema(
        summary=_("Een berichtontvanger gedeeltelijk wijzigen."),
        description=_("Een berichtontvanger gedeeltelijk wijzigen."),
    ),
    destroy=extend_schema(
        summary=_("Een berichtontvanger verwijderen"),
        description=_("Een berichtontvanger verwijderen"),
    ),
)
class BerichtOntvangerViewSet(viewsets.ModelViewSet):
    queryset = BerichtOntvanger.objects.all()
    serializer_class = BerichtOntvangerSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
