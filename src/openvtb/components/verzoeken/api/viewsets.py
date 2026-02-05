from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from vng_api_common.pagination import DynamicPageSizePagination

from openvtb.components.verzoeken.constants import VerzoekTypeVersionStatus

from ..models import Verzoek, VerzoekType, VerzoekTypeVersion
from .serializers import (
    VerzoekSerializer,
    VerzoekTypeSerializer,
    VerzoekTypeVersionSerializer,
)
from .utils import NestedViewSetMixin, verzoektype_uuid_param


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle verzoeken aan."),
        description=_("Vraag alle verzoeken aan."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifiek verzoek opvragen."),
        description=_("Een specifiek verzoek opvragen."),
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
    queryset = Verzoek.objects.select_related(
        "verzoek_type", "betaling", "bron"
    ).prefetch_related("bijlagen")
    serializer_class = VerzoekSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle verzoektypen aan."),
        description=_("Vraag alle verzoektypen aan."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifiek verzoektype opvragen."),
        description=_("Een specifiek verzoektype opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een verzoektype aan."),
        description=_("Maak een verzoektype aan."),
    ),
    update=extend_schema(
        summary=_("Volledig verzoektype wijzigen."),
        description=_("Volledig verzoektype wijzigen."),
    ),
    partial_update=extend_schema(
        summary=_("Een verzoektype gedeeltelijk wijzigen."),
        description=_("Een verzoektype gedeeltelijk wijzigen."),
    ),
    destroy=extend_schema(
        summary=_("Een verzoektype verwijderen"),
        description=_("Een verzoektype verwijderen"),
    ),
)
class VerzoekTypeViewSet(viewsets.ModelViewSet):
    queryset = VerzoekType.objects.prefetch_related("versions").order_by("-pk")
    serializer_class = VerzoekTypeSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"


@extend_schema_view(
    list=extend_schema(
        summary=_("Vraag alle verzoektypen versies aan."),
        description=_("Vraag alle verzoektypen versies aan."),
        parameters=[verzoektype_uuid_param],
    ),
    retrieve=extend_schema(
        summary=_("Een specifiek verzoektype versie opvragen."),
        description=_("Een specifiek verzoektype versie opvragen."),
        parameters=[verzoektype_uuid_param],
    ),
    create=extend_schema(
        summary=_("Maak een verzoektype versie aan."),
        description=_("Maak een verzoektype versie aan."),
        parameters=[verzoektype_uuid_param],
    ),
    update=extend_schema(
        summary=_("Volledig verzoektype versie wijzigen."),
        description=_("Volledig verzoektype versie wijzigen."),
        parameters=[verzoektype_uuid_param],
    ),
    partial_update=extend_schema(
        summary=_("Een verzoektype versie gedeeltelijk wijzigen."),
        description=_("Een verzoektype versie gedeeltelijk wijzigen."),
        parameters=[verzoektype_uuid_param],
    ),
    destroy=extend_schema(
        summary=_("Een verzoektype versie verwijderen"),
        description=_("Een verzoektype versie verwijderen"),
        parameters=[verzoektype_uuid_param],
    ),
)
class VerzoekTypeVersionViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = VerzoekTypeVersion.objects.order_by("verzoek_type", "-version")
    serializer_class = VerzoekTypeVersionSerializer
    lookup_field = "version"
    lookup_url_kwarg = "verzoektype_version"
    permission_classes = (IsAuthenticated,)
    pagination_class = DynamicPageSizePagination

    def perform_destroy(self, instance):
        if instance.status != VerzoekTypeVersionStatus.DRAFT:
            raise serializers.ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        _("Only draft versions can be destroyed")
                    ]
                },
                code="non-draft-version-destroy",
            )

        super().perform_destroy(instance)
