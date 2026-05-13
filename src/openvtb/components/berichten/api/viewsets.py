from django.utils.translation import gettext_lazy as _

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from vng_api_common.pagination import DynamicPageSizePagination

from ..cloudevents import BERICHT_GEREGISTREERD, send_bericht_cloudevent
from ..models import Bericht
from .serializers import BerichtGeopendOpSerializer, BerichtSerializer

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
    partial_update=extend_schema(
        summary=_("Werk het veld 'geopendOp' van een bericht bij."),
        description=_("Werk het veld 'geopendOp' van een bericht bij."),
        request=BerichtGeopendOpSerializer,
        responses=BerichtSerializer,
    ),
)
class BerichtViewset(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Bericht.objects.prefetch_related("bijlagen")
    serializer_class = BerichtSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action == "partial_update":
            return BerichtGeopendOpSerializer
        return BerichtSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance

        logger.info("bericht_created", uuid=str(instance.uuid))
        send_bericht_cloudevent(BERICHT_GEREGISTREERD, instance)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            BerichtSerializer(
                instance, context={"request": request, "view": self}
            ).data,
            status=status.HTTP_200_OK,
        )
