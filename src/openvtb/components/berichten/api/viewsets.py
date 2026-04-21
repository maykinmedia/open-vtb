from django.utils.translation import gettext_lazy as _

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from vng_api_common.pagination import DynamicPageSizePagination

from openvtb.utils.cloudevents import process_cloudevent

from ..constants import BERICHT_GEREGISTREERD
from ..models import Bericht
from .serializers import BerichtSerializer

logger = structlog.stdlib.get_logger(__name__)


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

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance

        logger.info("bericht_created", uuid=str(instance.uuid))

        process_cloudevent(
            type_event=BERICHT_GEREGISTREERD,
            subject=str(instance.uuid),
            data={
                "onderwerp": instance.onderwerp,
                "publicatiedatum": instance.publicatiedatum,
                "ontvanger": instance.ontvanger,
            },
        )
