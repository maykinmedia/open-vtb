from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from vng_api_common.pagination import DynamicPageSizePagination

from ..constants import SoortTaak
from ..models import ExterneTaak
from .serializers import (
    BetaalTaakSerializer,
    ExterneTaakPolymorphicSerializer,
    FormulierTaakSerializer,
    GegevensUitvraagTaakSerializer,
)
from .utils import SoortTaakMixinView, make_inline_response


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle externe taken aan.",
        description="Vraag alle externe taken aan.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke externe taak aanvragen.",
        description="Een specifieke externe taak aanvragen.",
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"


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
        summary="Een specifieke betaal taak aanvragen.",
        description="Een specifieke betaal taak aanvragen.",
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
class BetaalTaakViewSet(SoortTaakMixinView, viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.BETAALTAAK


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle gegevensuitvraag taaken aan.",
        description="Vraag alle gegevensuitvraag taaken aan.",
        responses={
            200: make_inline_response(
                name_suffix="GegevensUitvraagTaakListResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=GegevensUitvraagTaakSerializer,
            )
        },
    ),
    retrieve=extend_schema(
        summary="Een specifieke gegevensuitvraag taak aanvragen.",
        description="Een specifieke gegevensuitvraag taak aanvragen.",
        responses={
            200: make_inline_response(
                name_suffix="GegevensUitvraagTaakRetrieveResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=GegevensUitvraagTaakSerializer,
            )
        },
    ),
    create=extend_schema(
        summary="Maak een gegevensuitvraag taak aan.",
        description="Maak een gegevensuitvraag taak aan.",
        request=make_inline_response(
            name_suffix="GegevensUitvraagTaakCreateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=GegevensUitvraagTaakSerializer,
            write=True,
        ),
        responses={
            201: make_inline_response(
                name_suffix="GegevensUitvraagTaakCreateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=GegevensUitvraagTaakSerializer,
            )
        },
    ),
    update=extend_schema(
        summary="Volledig gegevensuitvraag taak wijzigen.",
        description="Volledig gegevensuitvraag taak wijzigen.",
        request=make_inline_response(
            name_suffix="GegevensUitvraagTaakUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=GegevensUitvraagTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="GegevensUitvraagTaakUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=GegevensUitvraagTaakSerializer,
            )
        },
    ),
    partial_update=extend_schema(
        summary="Een gegevensuitvraag taak gedeeltelijk wijzigen.",
        description="Een gegevensuitvraag taak gedeeltelijk wijzigen.",
        request=make_inline_response(
            name_suffix="GegevensUitvraagTaakPartialUpdateRequest",
            parent_serializer_class=ExterneTaakPolymorphicSerializer,
            inner_serializer_class=GegevensUitvraagTaakSerializer,
            write=True,
        ),
        responses={
            200: make_inline_response(
                name_suffix="GegevensUitvraagTaakPartialUpdateResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=GegevensUitvraagTaakSerializer,
            )
        },
    ),
    destroy=extend_schema(
        summary="Een gegevensuitvraag taak verwijderen",
        description="Een gegevensuitvraag taak verwijderen",
        responses={
            204: None,
        },
    ),
)
class GegevensUitvraagTaakViewSet(SoortTaakMixinView, viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.GEGEVENSUITVRAAGTAAK


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle formulier taaken aan.",
        description="Vraag alle formulier taaken aan.",
        responses={
            200: make_inline_response(
                name_suffix="FormulierTaakListResponse",
                parent_serializer_class=ExterneTaakPolymorphicSerializer,
                inner_serializer_class=FormulierTaakSerializer,
            )
        },
    ),
    retrieve=extend_schema(
        summary="Een specifieke formulier taak aanvragen.",
        description="Een specifieke formulier taak aanvragen.",
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
class FormulierTaakViewSet(SoortTaakMixinView, viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.FORMULIERTAAK
