from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from vng_api_common.pagination import DynamicPageSizePagination

from ..constants import SoortTaak
from ..models import ExterneTaak
from .serializers import (
    ExterneTaakPolymorphicSerializer,
    ExterneTaakSerializer,
)


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
class ExterneTaakViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakSerializer
    pagination_class = DynamicPageSizePagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle betaal taaken aan.",
        description="Vraag alle betaal taaken aan.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke betaal taak aanvragen.",
        description="Een specifieke betaal taak aanvragen.",
    ),
    create=extend_schema(
        summary="Maak een betaal taak aan.",
        description="Maak een betaal taak aan.",
    ),
    update=extend_schema(
        summary="Volledig betaal taak wijzigen.",
        description="Volledig betaal taak wijzigen.",
    ),
    partial_update=extend_schema(
        summary="Een betaal taak gedeeltelijk wijzigen.",
        description="Een betaal taak gedeeltelijk wijzigen.",
    ),
    destroy=extend_schema(
        summary="Een betaal taak verwijderen",
        description="Een betaal taak verwijderen",
    ),
)
class BetaalTaakViewSet(viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.BETAALTAAK

    def get_queryset(self):
        return super().get_queryset().filter(taak_soort=self.taak_soort)


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle gegevensuitvraag taaken aan.",
        description="Vraag alle gegevensuitvraag taaken aan.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke gegevensuitvraag taak aanvragen.",
        description="Een specifieke gegevensuitvraag taak aanvragen.",
    ),
    create=extend_schema(
        summary="Maak een gegevensuitvraag taak aan.",
        description="Maak een gegevensuitvraag taak aan.",
    ),
    update=extend_schema(
        summary="Volledig gegevensuitvraag taak wijzigen.",
        description="Volledig gegevensuitvraag taak wijzigen.",
    ),
    partial_update=extend_schema(
        summary="Een gegevensuitvraag taak gedeeltelijk wijzigen.",
        description="Een gegevensuitvraag taak gedeeltelijk wijzigen.",
    ),
    destroy=extend_schema(
        summary="Een gegevensuitvraag taak verwijderen",
        description="Een gegevensuitvraag taak verwijderen",
    ),
)
class GegevensUitvraagTaakViewSet(viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.GEGEVENSUITVRAAGTAAK

    def get_queryset(self):
        return super().get_queryset().filter(taak_soort=self.taak_soort)


@extend_schema_view(
    list=extend_schema(
        summary="Vraag alle formulier taaken aan.",
        description="Vraag alle formulier taaken aan.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke formulier taak aanvragen.",
        description="Een specifieke formulier taak aanvragen.",
    ),
    create=extend_schema(
        summary="Maak een formulier taak aan.",
        description="Maak een formulier taak aan.",
    ),
    update=extend_schema(
        summary="Volledig formulier taak wijzigen.",
        description="Volledig formulier taak wijzigen.",
    ),
    partial_update=extend_schema(
        summary="Een formulier taak gedeeltelijk wijzigen.",
        description="Een formulier taak gedeeltelijk wijzigen.",
    ),
    destroy=extend_schema(
        summary="Een formulier taak verwijderen",
        description="Een formulier taak verwijderen",
    ),
)
class FormulierTaakViewSet(viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakPolymorphicSerializer
    pagination_class = DynamicPageSizePagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = "uuid"
    taak_soort = SoortTaak.FORMULIERTAAK

    def get_queryset(self):
        return super().get_queryset().filter(taak_soort=self.taak_soort)
