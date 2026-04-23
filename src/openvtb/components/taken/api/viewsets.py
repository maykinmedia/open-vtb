import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from vng_api_common.pagination import DynamicPageSizePagination

from openvtb.utils.cloudevents import process_cloudevent

from ..constants import EXTERNETAAK_GEREGISTREERD, SoortTaak
from ..models import ExterneTaak
from .serializers import (
    BetaalTaakSerializer,
    ExterneTaakPolymorphicSerializer,
    FormulierTaakSerializer,
    URLTaakSerializer,
)
from .utils import SoortTaakMixin, make_inline_response

logger = structlog.stdlib.get_logger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle externe taken aan.",
        description="Vraag alle externe taken aan.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke externe taak opvragen.",
        description="Een specifieke externe taak opvragen.",
    ),
    create=extend_schema(
        summary="Maak een externe taak aan.",
        description="Maak een externe taak aan.",
    ),
    update=extend_schema(
        summary="Volledig externe taak wijzigen.",
        description="Volledig externe taak wijzigen.",
    ),
    partial_update=extend_schema(
        summary="Een externe taak gedeeltelijk wijzigen.",
        description="Een externe taak gedeeltelijk wijzigen.",
    ),
    destroy=extend_schema(
        summary="Een externe taak verwijderen",
        description="Een externe taak verwijderen",
    ),
)
class ExterneTaakViewSet(viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance

        logger.info("externetaak_created", uuid=str(instance.uuid))

        process_cloudevent(
            type_event=EXTERNETAAK_GEREGISTREERD,
            subject=str(instance.uuid),
            data={
                "taak_soort": instance.taak_soort,
                "titel": instance.titel,
                "status": instance.status,
                "einddatumHandelingsTermijn": instance.einddatum_handelings_termijn.isoformat()
                if instance.einddatum_handelings_termijn
                else "",
            },
        )


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle betaal taken aan.",
        description="Vraag alle betaal taken aan.",
        responses={
            200: make_inline_response(
                name_suffix="BetaalTaakListResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=BetaalTaakSerializer,
            )
        },
    ),
    retrieve=extend_schema(
        summary="Een specifieke betaal taak opvragen.",
        description="Een specifieke betaal taak opvragen.",
        responses={
            200: make_inline_response(
                name_suffix="BetaalTaakRetrieveResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=BetaalTaakSerializer,
            )
        },
    ),
    create=extend_schema(
        summary="Maak een betaal taak aan.",
        description="Maak een betaal taak aan.",
        request=make_inline_response(
            name_suffix="BetaalTaakCreateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=BetaalTaakSerializer,
            write=True,
        ),
        responses={
            201: make_inline_response(
                name_suffix="BetaalTaakCreateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=BetaalTaakSerializer,
            )
        },
    ),
    update=extend_schema(
        summary="Volledig betaal taak wijzigen.",
        description="Volledig betaal taak wijzigen.",
        request=make_inline_response(
            name_suffix="BetaalTaakUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=BetaalTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="BetaalTaakUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=BetaalTaakSerializer,
            )
        },
    ),
    partial_update=extend_schema(
        summary="Een betaal taak gedeeltelijk wijzigen.",
        description="Een betaal taak gedeeltelijk wijzigen.",
        request=make_inline_response(
            name_suffix="BetaalTaakPartialUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=BetaalTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="BetaalTaakPartialUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=BetaalTaakSerializer,
            )
        },
    ),
    destroy=extend_schema(
        summary="Een betaal taak verwijderen",
        description="Een betaal taak verwijderen",
        responses={
            204: None,
        },
    ),
)
class BetaalTaakViewSet(SoortTaakMixin, viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.BETAALTAAK


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle url taken aan.",
        description="Vraag alle url taken aan.",
        responses={
            200: make_inline_response(
                name_suffix="URLTaakListResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=URLTaakSerializer,
            )
        },
    ),
    retrieve=extend_schema(
        summary="Een specifieke url taak opvragen.",
        description="Een specifieke url taak opvragen.",
        responses={
            200: make_inline_response(
                name_suffix="URLTaakRetrieveResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=URLTaakSerializer,
            )
        },
    ),
    create=extend_schema(
        summary="Maak een url taak aan.",
        description="Maak een url taak aan.",
        request=make_inline_response(
            name_suffix="URLTaakCreateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=URLTaakSerializer,
            write=True,
        ),
        responses={
            201: make_inline_response(
                name_suffix="URLTaakCreateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=URLTaakSerializer,
            )
        },
    ),
    update=extend_schema(
        summary="Volledig url taak wijzigen.",
        description="Volledig url taak wijzigen.",
        request=make_inline_response(
            name_suffix="URLTaakUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=URLTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="URLTaakUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=URLTaakSerializer,
            )
        },
    ),
    partial_update=extend_schema(
        summary="Een url taak gedeeltelijk wijzigen.",
        description="Een url taak gedeeltelijk wijzigen.",
        request=make_inline_response(
            name_suffix="URLTaakPartialUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=URLTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="URLTaakPartialUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=URLTaakSerializer,
            )
        },
    ),
    destroy=extend_schema(
        summary="Een url taak verwijderen",
        description="Een url taak verwijderen",
        responses={
            204: None,
        },
    ),
)
class URLTaakViewSet(SoortTaakMixin, viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.URLTAAK


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle formulier taken aan.",
        description="Vraag alle formulier taken aan.",
        responses={
            200: make_inline_response(
                name_suffix="FormulierTaakListResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=FormulierTaakSerializer,
            )
        },
    ),
    retrieve=extend_schema(
        summary="Een specifieke formulier taak opvragen.",
        description="Een specifieke formulier taak opvragen.",
        responses={
            200: make_inline_response(
                name_suffix="FormulierTaakRetrieveResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=FormulierTaakSerializer,
            )
        },
    ),
    create=extend_schema(
        summary="Maak een formulier taak aan.",
        description="Maak een formulier taak aan.",
        request=make_inline_response(
            name_suffix="FormulierTaakCreateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=FormulierTaakSerializer,
            write=True,
        ),
        responses={
            201: make_inline_response(
                name_suffix="FormulierTaakCreateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=FormulierTaakSerializer,
            )
        },
    ),
    update=extend_schema(
        summary="Volledig formulier taak wijzigen.",
        description="Volledig formulier taak wijzigen.",
        request=make_inline_response(
            name_suffix="FormulierTaakUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=FormulierTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="FormulierTaakUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=FormulierTaakSerializer,
            )
        },
    ),
    partial_update=extend_schema(
        summary="Een formulier taak gedeeltelijk wijzigen.",
        description="Een formulier taak gedeeltelijk wijzigen.",
        request=make_inline_response(
            name_suffix="FormulierTaakPartialUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=FormulierTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="FormulierTaakPartialUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=FormulierTaakSerializer,
            )
        },
    ),
    destroy=extend_schema(
        summary="Een formulier taak verwijderen",
        description="Een formulier taak verwijderen",
        responses={
            204: None,
        },
    ),
)
class FormulierTaakViewSet(SoortTaakMixin, viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.FORMULIERTAAK
