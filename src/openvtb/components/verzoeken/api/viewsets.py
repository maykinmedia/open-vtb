from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework_nested.viewsets import NestedViewSetMixin
from vng_api_common.pagination import DynamicPageSizePagination

from ..models import Verzoek, VerzoekType, VerzoekTypeVersion
from .serializers import (
    VerzoekSerializer,
    VerzoekTypeSerializer,
    VerzoekTypeVersionSerializer,
)
from .utils import verzoektype_uuid_param


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle Vraag alle verzoeken aan taken aan."),
        description=_("Vraag alle verzoeken aan."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke verzoek opvragen."),
        description=_("Een specifieke verzoek opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een verzoek aan."),
        description=_("Maak een verzoek aan."),
    ),
    update=extend_schema(
        summary=_("Volledig verzoek wijzigen."),
        description=_("Volledig verzoek wijzigen."),
    ),
    partial_update=extend_schema(
        summary=_("Een verzoek gedeeltelijk wijzigen."),
        description=_("Een verzoek gedeeltelijk wijzigen."),
    ),
    destroy=extend_schema(
        summary=_("Een verzoek verwijderen"),
        description=_("Een verzoek verwijderen"),
    ),
)
class VerzoekViewSet(viewsets.ModelViewSet):
    queryset = Verzoek.objects.all()
    serializer_class = VerzoekSerializer
    pagination_class = DynamicPageSizePagination
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle Vraag alle verzoeken type aan taken aan."),
        description=_("Vraag alle verzoeken type aan."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke verzoek type opvragen."),
        description=_("Een specifieke verzoek type opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een verzoek type aan."),
        description=_("Maak een verzoek type aan."),
    ),
    update=extend_schema(
        summary=_("Volledig verzoek type wijzigen."),
        description=_("Volledig verzoek type wijzigen."),
    ),
    partial_update=extend_schema(
        summary=_("Een verzoek type gedeeltelijk wijzigen."),
        description=_("Een verzoek type gedeeltelijk wijzigen."),
    ),
    destroy=extend_schema(
        summary=_("Een verzoek type verwijderen"),
        description=_("Een verzoek type verwijderen"),
    ),
)
class VerzoekTypeViewSet(viewsets.ModelViewSet):
    queryset = VerzoekType.objects.prefetch_related("versions").order_by("-pk")
    serializer_class = VerzoekTypeSerializer
    pagination_class = DynamicPageSizePagination
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle verzoeken type versie aan taken aan."),
        description=_("Vraag alle verzoeken type versie aan."),
        parameters=[verzoektype_uuid_param],
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke verzoek type versie opvragen."),
        description=_("Een specifieke verzoek type versie opvragen."),
        parameters=[verzoektype_uuid_param],
    ),
    create=extend_schema(
        summary=_("Maak een verzoek type versie aan."),
        description=_("Maak een verzoek type versie aan."),
        parameters=[verzoektype_uuid_param],
    ),
    update=extend_schema(
        summary=_("Volledig verzoek type versie wijzigen."),
        description=_("Volledig verzoek type versie wijzigen."),
        parameters=[verzoektype_uuid_param],
    ),
    partial_update=extend_schema(
        summary=_("Een verzoek type versie gedeeltelijk wijzigen."),
        description=_("Een verzoek type versie gedeeltelijk wijzigen."),
        parameters=[verzoektype_uuid_param],
    ),
    destroy=extend_schema(
        summary=_("Een verzoek type versie verwijderen"),
        description=_("Een verzoek type versie verwijderen"),
        parameters=[verzoektype_uuid_param],
    ),
)
class VerzoekTypeVersionViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = VerzoekTypeVersion.objects.order_by("verzoek_type", "-version")
    serializer_class = VerzoekTypeVersionSerializer
    lookup_field = "version"
    lookup_url_kwarg = "verzoektype_version"
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    pagination_class = DynamicPageSizePagination
